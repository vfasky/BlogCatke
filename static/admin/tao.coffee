define (require, exports, module) ->

    # 加载 bootstrap
    jQuery = require 'bootstrap'
    Modal  = require 'bootstrap/modal'

    # 主容器
    main   = jQuery '#select-goods'

    # 分页组件
    Pagination = require './pagination'

    _show_info = (data, box) ->
        if data.comments and data.info and false == data.is_show
            box.find('.load').remove()
            data.is_show = true
            comments = []
            for v in data.comments ? []
                comments.push "
                <div class='comment-box'>
                    <div class='user'>
                        <img src='#{v.user.avatar}' alt=''>
                        #{v.user.nick}
                    </div>
                    <div class='comment'>
                        #{v.content}
                    </div>
                </div>
                "

            content = "
            <div class='item-info'>
                <div class='comments'>
                    #{comments.join('')}
                </div>
                <div class='desc'>
                    <img class='avatar' src='#{data.pic_url}' alt=''/>
                    <p>
                        <strong class='price'>售价：￥#{data.price} 
                        / 返佣：￥#{ data.commission } </strong>
                    </p>
                    <p>
                        卖家：#{data.nick} (#{data.item_location})
                        &nbsp; / &nbsp; 
                        信用： #{data.seller_credit_score} 级
                    </p>
                </div>
                <div class='html'>
                    <textarea style='width:720px;'>
                    #{data.info.desc}
                    </textarea>
                </div>
            </div>
            "

            pop = new Modal.Base({
                header : data.title ,
                body : content ,
                footer : "
                <button class='btn btn-primary add-goods'>入库</button>
                "
            })

            pop.dom.find('button.add-goods').click ->
                #console.log data
                pop.remove()
                jQuery.post('/admin/tao-add', data : JSON.stringify(data) )
                false

            pop.dom.width(1000)
            pop.dom.css(
                marginLeft : - 500 ,
                marginTop : '0' ,
                top : 10
            ).find('.modal-body').css(
                maxHeight : jQuery(window).height() - 160
            )
            pop.dom.find('textarea').height(jQuery(window).height() - 220)
            pop.show()

            KindEditor.create(pop.dom.find('textarea'),
                themeType : 'simple' ,
                resizeType : 0 ,
                allowImageUpload : false ,
                items : [
                        'fullscreen', 'source', 'preview' , '|' , 'fontsize', 'forecolor', 'hilitecolor', 'bold', 'italic', 'underline',
                        'removeformat', '|', 'justifyleft', 'justifycenter', 'justifyright', 'insertorderedlist',
                        'insertunorderedlist', '|', 'image', 'link']

            )
    # 查看商品详情
    show_info = (data, box) ->
        box.append "
        <div class='load'>loading...</div>
        "

        data.info = false
        data.comments = false
        data.is_show = false
        #取详细
        jQuery.get('/admin/tao-details', num_iids : data.num_iid, (json) ->
            if json.success
                data.info = json.data[0]
                _show_info(data, box)
            else
                new Modal.Alert({
                    content : json.msg
                })
        )
        #取评论
        jQuery.get('/admin/tao-comments', num_iid : data.num_iid, (json) ->
            if json.success
                data.comments = json.data.comments ? []
                _show_info(data, box)
            else
                # new Modal.Alert({
                #     content : '评论出错 ：' + json.msg
                # })
                data.comments = []
                _show_info(data, box)
        )


    list_goods = (post, data, page) ->
        dom            = jQuery '#goods-list'
        pagination_wrap = jQuery '.pagination-wrap'

        #clear
        dom.find('.box').remove()
        pagination_wrap.find('.pagination').remove()
        # 分页
        pagination = new Pagination(data.total_results, page, 40)
        pagination_dom = pagination.render (page) ->
            show_goods(post, page)

        pagination_dom.appendTo pagination_wrap

     
        for v in data.taobaoke_items.taobaoke_item
            box = jQuery "
            <div class='box' num_iid='#{v.num_iid}'>
                <img src='#{v.pic_url}' alt='' >
                <div class='commission label label-warning'>返佣：#{v.commission_rate / 100} % = ￥ #{ v.commission }</div>
                <span class='price'> ￥ #{v.price}</span>
                <strong title='#{v.title}'>#{v.title}</strong>
                <hr/>
                <span class='badge badge-success'>
                    <i class='icon-shopping-cart icon-white'></i>
                    #{v.volume }
                </span>  
                <a class='btn btn-mini' href='#{v.click_url}' target='_blank'>
                    <i class='icon-map-marker'></i>
                </a>  
                <a class='btn btn-mini' href='#{v.shop_click_url}' target='_blank'>
                    <i class='icon-home'></i>
                </a>   
                
            </div>
            "

            bind = (data, box) ->
                box.find('img').click ->
                    show_info(data, box)
                    false
            bind(v, box)

            box.appendTo dom

    bind_sort = ->
        main.find('.sort-btn .dropdown-menu a').click ->
            that = jQuery @
            main.find('.sort-btn').attr('sort' , that.attr('data'))
                .find('button').html(that.html() + ' <span class="caret"></span>')

            return false

    show_goods = (data, page = 1) ->
        data.page = page
        jQuery.post(data.url, data, (json)->
            if json.success
                list_goods(data, json.goods, json.page)
        , 'json')


    # 搜索绑定
    bind_search = ->
        main.find('.search-form').submit ->
            data = 
                keyword    : jQuery.trim(main.find('.keyword').val()),
                cid        : main.find('.items-btn').attr('cid') ,
                sort       : main.find('.sort-btn').attr('sort') ,
                url        : main.find('.search-goods').attr('url') ,
                commission_start : main.find('.commission-btn').attr('start')
                commission_end   : main.find('.commission-btn').attr('end') ,

            show_goods data
            return false
            

    # 绑定佣金
    bind_select_commission = ->
        btn_dom = main.find('.commission-btn')
        box_dom = main.find('.commission-box')

        btn_dom.toggle(->
            box_dom.css('left', btn_dom.position().left).show()
        ,->
            box_dom.hide()
        )

        box_dom.find('button').click ->
            that  = jQuery @
            start = box_dom.find('.start').val()
            end   = box_dom.find('.end').val()

            if start == '' or end == ''
                btn_dom.attr('start',0).attr('end',0)
                btn_dom.find('span').html "佣金"
            else
                btn_dom.attr('start',start).attr('end',end)
                btn_dom.find('span').html "#{start} ~ #{end} %"
            box_dom.hide()



    # 选择分类
    bind_select_item = ->
        # 绑定分类选择
        main.find('.items-btn').click ->
            main.find('.items-list').slideToggle()

        main.find('.items-list').find('a').click ->
            that = jQuery @
            main.find('.items-btn span').html that.html()
            main.find('.items-btn').attr('cid', that.attr('cid'))
            main.find('.items-list').slideToggle().find('li').show()
            main.find('.items-list').find('[type=search]').val('')
          
            return false

        # 实现搜索
        search_time = false
        main.find('.items-list').find('[type=search]').keyup ->
            that = jQuery @
            clearTimeout search_time if search_time
            search_time = setTimeout( ( ->
                search = jQuery.trim that.val() 
                if search == ''
                    main.find('.items-list').find('li').show()
                    return
                main.find('.items-list').find('a').each ->
                    itemDom = jQuery @
                    if itemDom.text().indexOf(search) != -1
                        itemDom.parent().show()
                    else
                        itemDom.parent().hide() 
            ), 500 )



    do ->
        bind_select_item()
        #main.find('.items-btn').click()
        bind_sort()
        bind_select_commission()
        bind_search()
    return