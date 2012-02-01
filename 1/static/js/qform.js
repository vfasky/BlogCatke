/**
 * Created by PyCharm.
 * User: vfasky
 * Date: 11-12-24
 * Time: 下午10:27
 * 生成表单,基于 bootstrap
 */
(function(jQuery , host){
    /**
     * 验证规则
     */
    var Validators = function(){

        /**
         * 是否邮箱
         * @param str
         */
        var isEmail = function(str)
        {
            var emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$/i;
            var ret = emailRegex.test(str);

            if( ret )
            {
                return { 'success' : true }
            }
            return { 'success' : false , 'msg' : '邮箱格式错误' }
        };

        /**
         * 是否数字
         * @param str
         */
        var isNumber = function(str)
        {
            var decimalRegex = /^\-?[0-9]*\.?[0-9]+$/;
            var ret =  decimalRegex.test(str);

            if( ret )
            {
                return { 'success' : true }
            }
            return { 'success' : false , 'msg' : '只能为数字' }
        };

        /**
         * 是否网址
         * @param str
         */
        var isUrl = function(str)
        {
            var url = /^http:\/\/[A-Za-z0-9]+\.[A-Za-z0-9]+[\/=\?%\-&_~`@[\]\':+!]*([^<>\"\"])*$/;
            var ret = url.test(str);

            if( ret )
            {
                return { 'success' : true }
            }
            return { 'success' : false , 'msg' : '网址格式错误' }
        };

        /**
         * 不为空
         * @param str
         */
        var notEmpty = function(str)
        {
            str = str.replace(/^\s+|\s+$/g,'');
            var ret =  '' == str ? false : true;

            if( ret )
            {
                return { 'success' : true }
            }
            return { 'success' : false , 'msg' : '不能为空' }
        };

        return {
            isEmail : isEmail ,
            isNumber : isNumber ,
            isUrl : isUrl ,
            notEmpty : notEmpty
        };
    }();

    /**
     * 表单组件基类
     * @param args
     */
    var FormWidgetBase = function( args , undef ){
        this._name  = args.name || '';
        this._label = args.label || '';
        this._value = args.value || '';
        this._type  = args.type || 'text';
        this._attrs = args.attrs || {};
        this._validators = args.validators || [];

        /**
         * 闭包
         */
        var _self = this;

        /**
         * 表单行对象
         */
        this.rowDom = false;

        /**
         * 构造行对象
         */
        this.build = function(){
            var tpl = '<div class="clearfix">' +
                        '<label >' + this._label + '</label>' +
                        '<div class="input">' +
                            '<input  class="span5" type="' + this._type + '">'+
                        '</div>'+
                      '</div>';

            this.rowDom = jQuery( tpl );
            for( k in this._attrs)
            {
                this.rowDom.find('input').attr(k , this._attrs[k]);
            }

            this.rowDom.find('input').val( this._value )
                                      .attr('name' , this._name);

            return this.rowDom;
        };

        this.getName = function()
        {
            return this._name;
        };

        this.setValue = function( value )
        {
            this.rowDom.find('input').val( value );
            this.hideError();
        };

        this.getValue = function()
        {
            return this.rowDom.find('input').val();
        };

        /**
         * 显示错误信息
         */
        this.showError = function( msg )
        {
            this.rowDom.find('.error-msg').remove();

            this.rowDom.addClass('error');
            this.rowDom.find('input').addClass('error');
            this.rowDom.find('.input').append('<span class="help-inline error-msg">'+msg+'</span>');
        };

        /**
         * 隐藏错误信息
         */
        this.hideError = function()
        {
            this.rowDom.removeClass('error');
            this.rowDom.find('input').removeClass('error');
            this.rowDom.find('.error-msg').remove();
        };

        /**
         * 验证行，成功后回调
         * @param callback
         */
        this.validators = function( callback )
        {
            callback = callback || function(){};
            var value = this.getValue();

            var isPass = true;
            jQuery.each( this._validators , function( k , v){
                if( jQuery.isFunction( Validators[v] ) )
                {
                    var ret = Validators[v]( value );
                    isPass = ret.success;

                    if( false == isPass )
                    {
                        _self.showError( ret.msg );
                        return false;
                    }
                }
            } );

            if( isPass )
            {
                this.hideError();
                callback();
            }
        };


    };

    /**
     * 表单组件
     */
    var FormWidgets = {};

    /**
     * 隐藏域
     * @param args
     */
    FormWidgets['hidden'] = function( args )
    {
        FormWidgetBase.call(this , args);

        /**
         * 构造行对象
         */
        this.build = function(){
            var tpl = '<input  class="span5" type="' + this._type + '">';

            this.rowDom = jQuery( tpl );
            for( k in this._attrs)
            {
                this.rowDom.attr(k , this._attrs[k]);
            }

            this.rowDom.val( this._value )
                         .attr('name' , this._name);

            return this.rowDom;
        };

        this.setValue = function( value )
        {
            this.rowDom.val( value );
        };

        this.getValue = function()
        {
            return this.rowDom.val();
        };

        /**
         * 显示错误信息
         */
        this.showError = function( msg )
        {
            alert( this._name + ' : ' +  msg);
        };

        this.hideError = function(){};

        this.build();
    };

    /**
     * 下拉框
     * @param args
     */
    FormWidgets['select'] = function( args )
    {
        FormWidgetBase.call(this , args);

        var _self = this;

        /**
         * 构造行对象
         */
        this.build = function(){
            var tpl = '<div class="clearfix">'+
                '<label>'+ this._label + '</label>'+
                '<div class="input"><select name="'+ _self._name +'"></select></div>' +
                '</div>';

            this.rowDom = jQuery( tpl );

            for( k in this._attrs)
            {
                _self.rowDom.find('select').attr(k , _self._attrs[k]);
            }

            args.data = args.data || [];

            jQuery.each( args.data , function(k , v){

                var option = jQuery('<option value="'+ v.value +'">'+ v.label +'</option>');
                option.appendTo( _self.rowDom.find('select') );
            } );

            this.setValue( this._value )

            return this.rowDom;
        };

        this.setValue = function( values )
        {
            this.rowDom.find('select').val( values )
        };

        this.getValue = function()
        {
            return this.rowDom.find('select').val();
        };

        /**
         * 显示错误信息
         */
        this.showError = function( msg )
        {
            this.rowDom.find('.error-msg').remove();

            this.rowDom.addClass('error');
            this.rowDom.find('select').addClass('error');
            this.rowDom.find('.input').append('<span class="help-inline error-msg">'+msg+'</span>');
        };

        /**
         * 隐藏错误信息
         */
        this.hideError = function()
        {
            this.rowDom.removeClass('error');
            this.rowDom.find('select').removeClass('error');
            this.rowDom.find('.error-msg').remove();
        };

        this.build();
    }

    /**
     * 多选框
     * @param args
     */
    FormWidgets['checkbox'] = function( args )
    {
        FormWidgetBase.call(this , args);

        var _self = this;

        /**
         * 构造行对象
         */
        this.build = function(){
            var tpl = '<div class="clearfix">'+
                            '<label>'+ this._label + '</label>'+
                            '<div class="input"><ul class="inputs-list"></ul></div>' +
                       '</div>';
            
            this.rowDom = jQuery( tpl );

            args.data = args.data || [];

            jQuery.each( args.data , function(k , v){
                var li = jQuery('<li><label><input type="checkbox" value="'+ v.value +'" name="'+ _self._name +'"><span>'+ v.label +'</span></li>');

                for( k in this._attrs)
                {
                    li.find('input').attr(k , _self._attrs[k]);
                }
                li.appendTo( _self.rowDom.find('.inputs-list') );
            } );

            this.setValue( this._value )

            return this.rowDom;
        };

        this.setValue = function( values )
        {
            if( false == jQuery.isArray( values ) )
            {
                values = [ values ]
            }

            this.rowDom.find('.inputs-list input').each(function(){
                var input = jQuery(this).attr('checked' , false);
                jQuery.each( values , function(k , v){
                    if( v == input.val() )
                    {
                        input.attr('checked' , true);
                        return false;
                    }
                });
            });

        };

        this.getValue = function()
        {
            var value = [];
            this.rowDom.find('.inputs-list input:checked').each(function(){
                value[ value.length ] = jQuery(this).val()
            });
            return value;
        };

        /**
         * 显示错误信息
         */
        this.showError = function( msg )
        {
            this.rowDom.find('.error-msg').remove();
            this.rowDom.addClass('error');
            this.rowDom.find('.input').append('<span class="help-block error-msg">'+msg+'</span>');
        };

        /**
         * 隐藏错误信息
         */
        this.hideError = function()
        {
            this.rowDom.removeClass('error');
            this.rowDom.find('.error-msg').remove();
        };

        this.build();
    };

    /**
     * 多行文本框
     * @param args
     */
    FormWidgets['textarea'] = function( args )
    {
        FormWidgetBase.call(this , args);

        /**
         * 构造行对象
         */
        this.build = function(){
            var tpl = '<div class="clearfix">' +
                '<label >' + this._label + '</label>' +
                '<div class="input">' +
                '<textarea rows="3"   class="xxlarge"></textarea>'+
                '</div>'+
                '</div>';

            this.rowDom = jQuery( tpl );
            for( k in this._attrs)
            {
                this.rowDom.find('textarea').attr(k , this._attrs[k]);
            }

            this.rowDom.find('textarea').val( this._value )
                .attr('name' , this._name);

            return this.rowDom;
        };

        this.setValue = function( value )
        {
            this.rowDom.find('textarea').val( value );
            this.hideError();
        };

        this.getValue = function()
        {
            return this.rowDom.find('textarea').val();
        };

        /**
         * 显示错误信息
         */
        this.showError = function( msg )
        {
            this.rowDom.find('.error-msg').remove();

            this.rowDom.addClass('error');
            this.rowDom.find('textarea').addClass('error');
            this.rowDom.find('.input').append('<span class="help-inline error-msg">'+msg+'</span>');
        };

        /**
         * 隐藏错误信息
         */
        this.hideError = function()
        {
            this.rowDom.removeClass('error');
            this.rowDom.find('textarea').removeClass('error');
            this.rowDom.find('.error-msg').remove();
        };

        this.build();
    };

    /**
     * 文本框
     * @param args
     */
    FormWidgets['text'] = function( args )
    {
        FormWidgetBase.call(this , args);
        this.build();
    };

    /**
     * 密码框
     * @param args
     */
    FormWidgets['password'] = function( args )
    {
        FormWidgetBase.call(this , args);
        this.build();
    };

    /**
     * 表单
     * @param attr 表单属性
     * @param rules 元素规则
     * @param buts 按钮属性
     * @param undef
     */
    var Form = function( attr ,  rules , buts , undef ){
        /**
         * 规则
         */
        var _rules = rules || [];

        //表单属性
        attr = attr || {};
        /**
         * 提交地址
         */
        var _url = attr.url || '';
        var _method = attr.method || 'post';

        /**
         * 表单元素
         */
        var _item = [];

        /**
         * 表单组件
         */
        var _widgets = [];

        var _tpl = '<form class="form-stacked" action="'+ _url +'" method="'+_method+'"><fieldset></fieldset><div class="actions"></div></form>';

        /**
         * 表单dom
         */
        var _dom = jQuery( _tpl );

        /**
         * 表单值
         */
        var _values = {};

        var _self = this;

        var _isPass = false;

        /**
         * 添加组件
         * @param rule
         */
        this.add = function( rule )
        {
            rule = rule || {};

            if( rule.type && FormWidgets[ rule.type ] )
            {
                var item = new FormWidgets[ rule.type ]( rule );
                _widgets[ _widgets.length ] = item;
                return item;
            }
            return false;
        };

        /**
         * 设置表单值
         * @param values
         */
        this.setValues = function( values )
        {
            jQuery.each( _widgets , function( k , v){
                if( undef != values[ v.getName() ] )
                {
                    v.setValue( values[ v.getName() ] )
                }
            })
        }

        /**
         * 构造表单
         */
        this.build = function()
        {
            jQuery.each( _rules , function(k , v){

                var item = _self.add( v );
                if( item && item.rowDom )
                {
                    item.rowDom.appendTo( _dom.find('fieldset') );
                }
            } );

            if( buts != undef )
            {
                if( jQuery.isArray( buts ) )
                {
                    jQuery.each( buts , function(k , v){
                        v.type = v.type || 'submit';
                        v.label = v.label || '提交';
                        v.attr = v.attr || {};
                        var but = jQuery('<button class="btn" type="'+ v.type +'">'+ v.label +'</button>');
                        for( key in v.attr )
                        {
                            but.attr( key , v.attr[key] );
                        }
                        but.appendTo( _dom.find('.actions') );
                    } );
                }
            }

            //绑定提交事件
            _dom.bind('submit' ,function(){
                if( false == _isPass )
                {
                    _self.validators(function(){
                        _isPass = true;
                        _dom.submit();
                    })
                }
                return _isPass;
            });

            return _dom;
        };

        this.dom = function()
        {
            return _dom;
        }

        /**
         * 验证表单
         * @param callback
         */
        this.validators = function( callback )
        {
            callback = callback || function(){}
            _values = {};
            var passCount = 0;
            jQuery.each( _widgets , function( k , v){
                v.validators( function(){
                    _values[ v.getName() ] = v.getValue();
                    passCount ++;

                    if( passCount == _widgets.length )
                    {
                        callback( _values );
                    }
                } )
            } )
        };

        //构造表单
        this.build();
    };

    host.Qform = Form;
    host.Qvalidators = Validators;

})(jQuery , window);