/**
 * Created by PyCharm.
 * User: vfasky
 * Date: 12-1-18
 * Time: 上午11:10
 * To change this template use File | Settings | File Templates.
 */
var Qcore = Qcore || {};

/**
 * html 5 上传
 * @param cfg
 */
Qcore.xhrUpload = function( cfg ){
    var cfg = jQuery.extend( {
        file : false ,
        action : '' ,
        progress : function(){} ,
        success : function(){}

    } , cfg );

    if ( false == cfg.file )
    {
        return false;
    }
    var file   = cfg.file;
    var action = cfg.action;

    var xhr      = new XMLHttpRequest();
    var boundary = '------multipartformboundary' + (new Date).getTime();

    xhr.upload.addEventListener("progress", function (e) {
        cfg.progress( Math.round((e.loaded * 100) / e.total) )
    });

    xhr.open("POST", action , true);
    xhr.setRequestHeader("Content-Type", "multipart/form-data, boundary=" + boundary);
    xhr.setRequestHeader("Content-Length", file.size);
    xhr.setRequestHeader("Cache-Control", "no-cache");
    xhr.setRequestHeader('Content-Disposition', 'form-data; name=filedata; filename=' + encodeURIComponent(file.name))
    //发送两进制文件
    xhr.sendAsBinary = xhr.sendAsBinary || function(datastr) {
        var ords = Array.prototype.map.call(datastr, function(x) {
            return x.charCodeAt(0) & 0xFF;
        }),
            unit8Arr = new Uint8Array(ords);

        this.send(unit8Arr.buffer);
    };

    xhr.onreadystatechange = function(){
        if (xhr.readyState == 4){
            cfg.success( xhr.responseText )
        }
    };

    xhr.sendAsBinary(["--" + boundary,
        "Content-Disposition: form-data; name=\"filedata\"; filename=\"" + encodeURIComponent(file.name) + "\"",
        "Content-Type: " + file.type + "\r\n",
        cfg.data,
        "--" + boundary,
        "Content-Disposition: form-data; name=\"filename\"\r\n",
        encodeURIComponent(file.name),
        "--" + boundary + "--"].join("\r\n"));
}

//编辑器
Qcore.editor = function( editor ){
    var _editor = editor;
    var _self = this;

    //弹窗容器
    this.modelDom = jQuery('<div class="modal hide fade">' +
                                '<div class="modal-body">' +
                                    '<a href="#close-modal" class="close">&times;</a>' +
                                    '<div class="content"></div>' +
                                '</div>'+
                            '</div>');


    //组件
    this.widget = {};

    /**
     * 连接
     * @param markItUp
     */
    this.widget['link'] = function( markItUp ){


        var content = '<ul class="tabs">' +
            '<li class="active"><a href="#getUrl">插入连接</a></li>' +
            '<li><a href="#uploadFile">上传附件</a></li>' +
            '</ul>';

        content += '<div class="pill-content">' +
            '<div class="active" id="getUrl"></div>' +
            '<div id="uploadFile"></div>' +
            '</div>'

        _self.modelDom.find('.content .wrap').remove();
        _self.modelDom.find('.content').html('<div class="wrap"></div>')
        _self.modelDom.find('.content .wrap').html( content );

        //上传附件
        if (window.FileReader) {
            var dropBox = '<div id="drop_zone_file" class="drop_zone">将文件拖到这!</div>';
            _self.modelDom.find('#uploadFile').html( dropBox );

            var cnt = _self.modelDom.find('#drop_zone_file')[0];

            cnt.addEventListener('dragenter', function(){
                jQuery(this).addClass('alert-message')
            }, false);
            cnt.addEventListener('dragover', function(e){
                e.stopPropagation();
                e.preventDefault();
                return false;
            }, false);
            cnt.addEventListener('drop', function(e){
                e.stopPropagation();
                e.preventDefault();
                // 取文件列表
                var files = e.dataTransfer.files;
                var count = files.length;
                var isUpload = 0;
                var ul = jQuery('<ul></ul>').appendTo( _self.modelDom.find('#drop_zone_file').html('') )
                jQuery.each( files , function( k , file){

                    var size = ( file.size / 1024 / 1024 ).toFixed(2);
                    if( size < 10 )
                    {
                        var li = jQuery('<li></li>').appendTo( ul );
                        li.html(file.name + ' 上传 0%' );

                        var reader = new FileReader();

                        reader.onload = (function(theFile) {
                            return function(e) {

                                var xhrUpload = Qcore.xhrUpload({
                                    action :  '/admin/upload?name=' + encodeURIComponent(file.name) + '&type=' + file.type ,
                                    file : file ,
                                    data : reader.result,
                                    progress : function( p ){
                                        li.html(file.name + ' 上传 ' + p + '%' );
                                    } ,
                                    success : function( data ){
                                        isUpload++;
                                        if( isUpload == count )
                                        {
                                            _self.modelDom.modal('hide');
                                        }

                                        var json = jQuery.parseJSON( data );
                                        if( json.success )
                                        {
                                            code = "["+ file.name +"]("+ json.url +")\r\n";
                                            markItUp.textarea.value += code
                                        }
                                        else
                                        {
                                            Qalert( json.msg )
                                        }
                                    }
                                });

                            };
                        })(file);
                        reader.readAsBinaryString(file)

                    }
                    else
                    {
                        Qalert( '"' + file.name + '" 大于10M ,无法上传!' )
                    }


                });
            }, false);
        }
        else
        {
            var msg = '<div class="alert-message error"><p>你的浏览器不支持啊，同学! 支持的浏览器有: <a target="_blank" href="http://www.google.cn/chrome/">Chrome 6+</a> / <a target="_blank" href="http://firefox.com.cn/">Firefox 9+</a> </p></div>';
            _self.modelDom.find('#uploadPhoto').html( msg )
        }

        //插入连接
        //加入表单
        var form = new Qform( { url : '' } ,[
            {"name": "title", "value": null , "label": "标题", "attrs": {}, "validators": ["notEmpty"], "type": "text"} ,
            {"name": "url", "value": 'http://', "label": "地址", "attrs": {}, "validators": ["notEmpty"], "type": "text"}
        ] , [ {'label' : '插入'} ] );

        form.dom().unbind('submit').submit(function(){
            form.validators(function( values ){
                code = "["+ values['title'] +"]("+ values['url'] +")\r\n";
                markItUp.textarea.value += code
                _self.modelDom.modal('hide');
            });
            return false;
        });

        form.dom().appendTo( _self.modelDom.find('#getUrl') )

        _self.modelDom.find('.tabs').tabs();

        _self.modelDom.modal({
            'backdrop' : true ,
            'show' : true
        });
    }


    /**
     * 图片
     * @param editor 编辑器容器
     */
    this.widget['photo'] = function( markItUp ){

        var content = '<ul class="tabs">' +
                        '<li class="active"><a href="#uploadPhoto">从本地上传</a></li>' +
                        '<li><a href="#getPhoto">从远程地址获取</a></li>' +
                       '</ul>';

        content += '<div class="pill-content">' +
                      '<div class="active" id="uploadPhoto"></div>' +
                      '<div id="getPhoto"></div>' +
                   '</div>'

        _self.modelDom.find('.content .wrap').remove();
        _self.modelDom.find('.content').html('<div class="wrap"></div>')
        _self.modelDom.find('.content .wrap').html( content );

        //本地上传
        if (window.FileReader) {
            var dropBox = '<div id="drop_zone"  class="drop_zone">将文件拖到这!</div>';
            _self.modelDom.find('#uploadPhoto').html( dropBox );

            var cnt = _self.modelDom.find('#drop_zone')[0];
            var isImage = function(type) {
                switch (type) {
                    case 'image/jpeg':
                    case 'image/png':
                    case 'image/gif':
                    case 'image/bmp':
                    case 'image/jpg':
                        return true;
                    default:
                        return false;
                }
            };
            cnt.addEventListener('dragenter', function(){
                jQuery(this).addClass('alert-message')
            }, false);
            cnt.addEventListener('dragover', function(e){
                e.stopPropagation();
                e.preventDefault();
                return false;
            }, false);
            cnt.addEventListener('drop', function(e){
                e.stopPropagation();
                e.preventDefault();
                // 取文件列表
                var files = e.dataTransfer.files;
                var count = files.length;
                var isUpload = 0;
                var ul = jQuery('<ul></ul>').appendTo( _self.modelDom.find('#drop_zone').html('') )
                jQuery.each( files , function( k , file){

                    //判断是否图片
                    if( isImage( file.type ) )
                    {
                        var size = ( file.size / 1024 / 1024 ).toFixed(2);
                        if( size < 10 )
                        {
                            var li = jQuery('<li></li>').appendTo( ul );
                            li.html(file.name + ' 上传 0%' );

                            var reader = new FileReader();

                            reader.onload = (function(theFile) {
                                return function(e) {

                                    var xhrUpload = Qcore.xhrUpload({
                                        action :  '/admin/upload?name=' + encodeURIComponent(file.name) + '&type=' + file.type ,
                                        file : file ,
                                        data : reader.result,
                                        progress : function( p ){
                                            li.html(file.name + ' 上传 ' + p + '%' );
                                        } ,
                                        success : function( data ){
                                            isUpload++;
                                            if( isUpload == count )
                                            {
                                                _self.modelDom.modal('hide');
                                            }

                                            var json = jQuery.parseJSON( data );
                                            if( json.success )
                                            {
                                                code = "!["+ file.name +"]("+ json.url +")\r\n";
                                                markItUp.textarea.value += code
                                            }
                                            else
                                            {
                                                Qalert( json.msg )
                                            }
                                        }
                                    });

                                };
                            })(file);
                            reader.readAsBinaryString(file)

                        }
                        else
                        {
                            Qalert( '"' + file.name + '" 大于10M ,无法上传!' )
                        }
                    }

                });
            }, false);
        }
        else
        {
            var msg = '<div class="alert-message error"><p>你的浏览器不支持啊，同学! 支持的浏览器有: <a target="_blank" href="http://www.google.cn/chrome/">Chrome 6+</a> / <a target="_blank" href="http://firefox.com.cn/">Firefox 3.6+</a> </p></div>';
            _self.modelDom.find('#uploadPhoto').html( msg )
        }

        //远程地址获
        //加入表单
        var getPhotoForm = new Qform( { url : '' } ,[
            {"name": "url", "value": 'http://', "label": "图片地址", "attrs": {}, "validators": ["notEmpty"], "type": "text"} ,
            {"name": "desc", "value": null, "label": "描述", "attrs": {},  "type": "text"}
        ] , [ {'label' : '插入'} ] );

        getPhotoForm.dom().unbind('submit').submit(function(){
            getPhotoForm.validators(function( values ){
                code = "!["+ values['desc'] +"]("+ values['url'] +")\r\n";
                markItUp.textarea.value += code
                _self.modelDom.modal('hide');
            });
            return false;
        });

        getPhotoForm.dom().appendTo( _self.modelDom.find('#getPhoto') )

        _self.modelDom.find('.tabs').tabs();

        _self.modelDom.modal({
            'backdrop' : true ,
            'show' : true
        });


    }
};
