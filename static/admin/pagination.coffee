define (require, exports, module) ->

    # 加载 bootstrap
    jQuery = require 'bootstrap'

    class Pagination
        
        constructor: (@count,@current_page=1,@page_size=10,@max=10) ->
            @count        = Number(@count)
            @current_page = Number(@current_page)
            @count_page   = Math.ceil( @count / @page_size )

            if @current_page > @count_page
                @current_page = @count_page
            
            @next_page = @current_page + 1
            if @next_page >= @count_page
                @next_page = @count_page

            @prev_page = @current_page - 1
            if @prev_page < 1
                @prev_page = 1

        build_left: ->
            if @count_page < @max
                return [1...(@count_page + 1)]

            c_max = Math.ceil( @max / 2 )

            if @current_page <= c_max
                return [1...c_max]

            return [(@current_page - c_max)...@current_page]

        build_right: ->
            return [] if @count_page < @max

            c_max = Math.ceil( @max / 2 )
            if @current_page <= c_max
                return [c_max...(@max + 1)]
            if (@current_page + c_max) > @count_page
                return [@current_page...(@count_page + 1) ]

            return [@current_page...(@current_page + c_max) ]


        render: (callback)->
            return jQuery('<div class="pagination"></div>') if @count_page < 2

            list = @build_left()
            for v in @build_right()
                list.push v

            list_html = []
            for v in list
                if v != @current_page
                    list_html.push "<li class='page' page='#{v}'><a href='#'>#{v}</a></li>"
                else
                    list_html.push "<li class='active'><a href='#'>#{v}</a></li>"

            dom = jQuery "
                <div class='pagination'>
                    <ul>
                        <li class='prev'><a href='#'>«</a></li>
                            #{list_html.join('')}
                        <li class='next'><a href='#'>»</a></li>
                    </ul>
                </div>
            "

            dom.find('li.page').click ->
                callback Number(jQuery(@).attr('page'))
                return false

            dom.find('li.prev').click =>
                callback @prev_page
                return false

            dom.find('li.next').click =>
                callback @next_page
                return false

            dom

  
    Pagination