define (require, exports) ->
    jQuery = require '../bootstrap'

    class Base
        constructor: (args = header : '' , body : '' , footer : '') ->
            
            @dom = jQuery "
<div class='modal' role='dialog' aria-hidden='true'>
    <div class='modal-header'>
        <button type='button' class='close'>×</button>
        <h3>#{args.header}</h3>
    </div>
    <div class='modal-body'>
        #{args.body}
    </div>
    <div class='modal-footer'>
        #{args.footer}
    </div>
</div>
"
            @dom.find('.close').click =>
                @hide()

            @dom.modal(
                show : false
            )

            @init()

        init: ->
            false

        show: ->
            @dom.modal('show')

        hide: ->
            @dom.modal('hide')

        remove: ->
            @dom.modal('hide')
            @dom.remove()

    class Alert extends Base
        constructor: (args = {}) ->
            title = args.title ? '提示信息！'
            content = args.content ? ''
            buttons = "
            <a href='#' class='btn btn-primary confirm-yes'>确认</a>
            "

            @callback = args.callback ? ->

            super(
                header : title ,
                body : content ,
                footer : buttons
            )

        init: -> 
   
            @dom.find('.confirm-yes').click =>
                @remove()
                @callback(true)
                false

            @show()

        hide: ->
            @callback(false)
            @remove()
        
   


    class Confirm extends Base

        constructor: (args = {}) ->
            title = args.title ? '提示信息！'
            content = args.content ? '您确认执行此操作？'
            buttons = "
            <a href='#' class='btn confirm-no'>取消</a>
            <a href='#' class='btn btn-primary confirm-yes'>确认</a>
            "

            @callback = args.callback ? ->

            super(
                header : title ,
                body : content ,
                footer : buttons
            )

        init: ->
            @dom.find('.confirm-no').click =>
                @remove()
                @callback(false)
                false

            @dom.find('.confirm-yes').click =>
                @remove()
                @callback(true)
                false

        hide: ->
            @callback(false)
            @remove()
        
    
        

    exports.Base    = Base
    exports.Confirm = Confirm
    exports.Alert   = Alert
    return
    