define (require, exports) ->

    utils  = require './utils'
    jQuery = require 'jquery'

    # 验证
    Validators = 
        Email: (x, msg, callback) ->
            msg = msg ? '邮箱格式错误'
            ret = utils.Validators.is_email x
            return callback(success : true) if ret
            callback( success : false , msg : msg )

        Required: (x, msg, callback) ->
            msg = msg ? '不能为空'
            ret = !utils.Validators.is_empty x
            return callback(success : true) if ret
            callback( success : false , msg : msg )

        IPAddress: (x, msg, callback) ->
            msg = msg ? '格式错误'
            ret = utils.Validators.is_ip x
            return callback(success : true) if ret
            callback( success : false , msg : msg )

        URL: (x, msg, callback) ->
            msg = msg ? '格式错误'
            ret = utils.Validators.is_url x
            return callback(success : true) if ret
            callback( success : false , msg : msg )
            

    # 表单 element 基类
    class FormElementBase
        
        constructor: (args) ->
            @args        = args
            @_name       = args.name
            @_label      = args.label ? args.name
            @_filters    = args.filters ? []
            @_validators = args.validators ? []
            @_attr       = args.attr ? {}
            @_tip        = @_attr.tip ? ''
            @_data       = args.data ? []
            @_error      = null
            @_form       = args.form
            @_type       = 'text'
            @_value      = null
            @_dom        = false

            

            @init()

        init: ->


        build_dom: ->
            "<div class='controls'>
                <input type='#{@_type}' class='input-xlarge' name='#{@_name}' placeholder='#{@_label}'>
                <span class='help-inline'>#{@_tip}</span>
             </div>
            "

        build_wrap: ->
            "<div class='control-group'>
                <label class='control-label'>#{@_label}</label>
                #{@build_dom()}
             </div>
            "

        set_attr: ->
            input_dom = @_dom.find("[name=#{@_name}]")
            for k , v of @_attr
                if k == 'class'
                    input_dom.addClass(v)
                else
                    input_dom.attr(k,v)

            input_dom

        build: ->
            @_dom = jQuery(@build_wrap())
            @set_attr()
            @set_value @args.value
            @_dom

        show_error: (msg) ->
            if @_dom
                @_dom.addClass('error')
                     .find('.help-inline')
                     .html(msg)
                     .show()

        hide_error: ->
            if @_dom
                @_dom.removeClass('error')
                msg_dom = @_dom.find('.help-inline')
                if utils.Validators.is_empty @_tip
                    msg_dom.hide()
                else
                    msg_dom.html(@_tip).show()




        # 设置值，并执行过滤
        set_value : (value) ->
            if value != null
                if @_data.length == 0
                    for v in @_filters
                        if utils.Filters.hasOwnProperty v
                            value = utils.Filters[v] value

                    @_value = value

                    if @_dom
                        @_dom.find("[name=#{@_name}]").val(@_value)

                else
                    for v in @_data
                        if value == v
                            @_value = value
                            if @_dom
                                @_dom.find("[name=#{@_name}]").val(@_value)
                            return 

        get_value : ->
            @_dom.find("[name=#{@_name}]").val()

        validate : (callback) ->
            @hide_error()
            count = 0
            pass  = 0
            for v in @_validators
                if Validators.hasOwnProperty v.name
                    count = count + 1

            for v in @_validators
                if Validators.hasOwnProperty v.name
                    Validators[v.name](@_value, v.message, (ret) =>
                        if ret.success
                            pass = pass + 1
                            if pass == count
                                return callback @_value
                        else
                            @_form.error(@, ret.msg)
                    )

            if 0 == count
                callback @_value

    class Text extends FormElementBase


    class Password extends FormElementBase

        init: ->
            @_type = 'password'

    class Textarea extends FormElementBase
        init: ->
            @_type = 'textarea'

        build_dom: ->
            "<div class='controls'>
                <textarea name='#{@_name}' rows='3'></textarea>
                <span class='help-inline'>#{@_tip}</span>
             </div>
            "


    class Button extends FormElementBase

        init: ->
            @_type = 'button'

        build_wrap: ->
            "<button type='#{@_type}' name='#{@_name}' class='btn'>#{@_label}</button>"

        validate : (callback) ->
            callback @_value

    class Submit extends Button

        init: ->
            @_type = 'submit'

        build_wrap: ->
            "<button type='#{@_type}' name='#{@_name}' class='btn btn-primary'>#{@_label}</button>"

    class Hidden extends FormElementBase

        init: ->

            @_type = 'hidden'

        build_wrap: ->
            "<span><input type='#{@_type}' name='#{@_name}' /></span>"

    class Select extends FormElementBase

        init: ->
            @_type = 'select'

        build_dom: ->
            list = ""
            for v in @_data
                list = list + "<option value='#{v.value}'>#{v.label}</option>"

            "<div class='controls'>
                <select name='#{@_name}'>
                    #{list}
                </select>
                <span class='help-inline'>#{@_tip}</span>
             </div>
            "

    class Radio extends FormElementBase

        init: ->
            @_type = 'radio'

        build_dom: ->
            list = ""
            for v in @_data
                list = list + "
                <label class='checkbox inline'>
                    <input type='#{@_type}' name='#{@_name}' value='#{@_value}'> #{@_label} 
                </label>"

            "<div class='controls'>
                #{list}
                <span class='help-inline'>#{@_tip}</span>
             </div>
            "

        # 设置值，并执行过滤
        set_value : (value) ->
            return false if !@_dom
            @_dom.find("[name=#{@_name}]").attr('checked', false)
            if value != null
                for v in @_data
                    if value.toString() == v.value.toString()
                        @_value = v.value
                        @_dom.find("[value=#{v.value}]").attr('checked' , true)
                        return 

    class Checkbox extends FormElementBase

        init: ->
            @_type = 'checkbox'

        build_dom: ->
            list = ""
            for v in @_data
                list = list + "
                <label class='checkbox inline'>
                    <input type='#{@_type}' name='#{@_name}[]' value='#{v.value}'> #{v.label} 
                </label>"



            "<div class='controls'>
                #{list}
                <span class='help-inline'>#{@_tip}</span>
             </div>
            "

        # 设置值，并执行过滤
        set_value : (value) ->
            return false if !@_dom
            @_dom.find("[type=#{@_type}]").attr('checked', false)
            @_value = []
          
            for v in @_data
                for v2 in value
                    if v2.toString() == v.value.toString()
                        @_value.push v.value
                        @_dom.find("[value=#{v2}]").attr('checked', true)
                   

        get_value: ->
            value = []
            @_dom.find("input[type=#{@_type}]").each ->
                that = jQuery @
                if that.attr('checked')
                    value.push that.val()

            value
           

        validate : (callback) ->
            @hide_error()
            callback @_value

    Items = 
        Text : Text ,
        Password : Password ,
        Button : Button ,
        Submit : Submit ,
        Hidden : Hidden ,
        Select : Select ,
        Radio  : Radio ,
        Textarea : Textarea ,
        Checkbox : Checkbox ,

    

    class Form

        constructor: (args) ->

            @action  = args.action ? ''
            @enctype = args.enctype ? 'multipart/form-data'
            @method  = args.method ? 'POST'
            @args    = args

            @_elements = []
            @_buttons  = []
            @_values   = {}
            @_dom      = false
            @_is_pass  = false

            for v in args.elements
                @add(v.type, v)


        error: (item_obj, msg) ->
            item_obj.show_error msg

        add: (item, args) ->
            args.form = @
            item = utils.Filters.ucfirst item

            if Items.hasOwnProperty item
                if item in ['Button' , 'Submit']
                    @_buttons.push new Items[item](args)
                else
                    @_elements.push new Items[item](args) 

        submit: (callback) ->
            @_dom.submit =>
                @validate (values) ->
                    callback values
                return false

        build_dom: ->
            "<form action='#{@action}' enctype='#{@enctype}' method='#{@method}' />"
        
        validate: (callback)->
            check = 0
            @_is_pass = false
            for v in @_elements
                v.set_value v.get_value()
                v.validate (val) =>
                    check = check + 1
                    @_values[v._name] = val
                    if check == @_elements.length
                        @_is_pass = true
                        callback @_values


        build: ->
            @_dom = jQuery(@build_dom())
            for v in @_elements
                v.build().appendTo @_dom

            if @_buttons.length > 0
                button_wrap = jQuery('<div class="form-actions"></div>')
                for v in @_buttons
                    v.build().appendTo button_wrap
                button_wrap.appendTo @_dom

            # 绑定默认的提交
            @_dom.submit =>
                if false == @_is_pass
                    dom = @_dom
                    @validate (values) ->
                        dom.submit()
                return @_is_pass

            @_dom
    Form
