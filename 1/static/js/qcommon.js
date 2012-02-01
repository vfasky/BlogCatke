/**
 * Created by PyCharm.
 * User: vfasky
 * Date: 11-12-25
 * Time: 下午7:49
 * 封装一些常用组件
 */
(function( jQuery , host){
    /**
     * 表单弹窗
     * @param QForm
     */
    host.QformDialog = function(  QForm  )
    {
        //弹窗容器
        var modelDom = jQuery('<div class="modal hide fade">' +
            '<div class="modal-body">' +
            '<a href="#close-modal" class="close">&times;</a>' +
            '</div>'+
            '</div>');

        QForm.dom().appendTo( modelDom )
        modelDom.modal({ 'show' : false });
        return modelDom;
    }

    /**
     * 确认框
     * @param content
     * @param callback
     * @param title
     */
    host.Qconfirm = function( content , callback , title )
    {
        title = title || '请确认';
        callback = callback || function(){};

        var ret = false;

        var modelDom = jQuery('<div class="modal hide fade">' +
            '<div class="modal-header">' +
            '<a href="#close-modal" class="close">&times;</a>' +
            '<h3>'+ title +'</h3>'+
            '</div>'+
            '<div class="modal-body">' +
            '<div>'+ content +'</div>'+
            '</div>'+
            '<div class="modal-footer">'+
            '<a class="btn primary ok-btn"  href="#">确认</a>'+
            '<a class="btn secondary cancel-bth" href="#">取消</a>'+
            '</div>'+
            '</div>');

        modelDom.find('.modal-footer .ok-btn').click(function(){
            ret = true;
            modelDom.modal('hide');
            return false;
        });

        modelDom.find('.modal-footer .cancel-bth').click(function(){
            modelDom.modal('hide');
            return false;
        });

        modelDom.modal({
            'backdrop' : true ,
            'show' : true
        });

        modelDom.bind('hidden' , function(){
            callback( ret );
            modelDom.remove();
        });
    }

    /**
     * 弹窗
     * @param content
     * @param title
     * @param callback
     */
    host.Qalert = function( content , title , callback )
    {
        title = title || '提示信息';
        callback = callback || function(){};
        var modelDom = jQuery('<div class="modal hide fade">' +
                                '<div class="modal-header">' +
                                    '<a href="#close-modal" class="close">&times;</a>' +
                                    '<h3>'+ title +'</h3>'+
                                '</div>'+
                                '<div class="modal-body">' +
                                    '<div>'+ content +'</div>'+
                                '</div>'+
                                '<div class="modal-footer">'+
                                    '<a class="btn primary ok-btn"  href="#">确认</a>'+
                                '</div>'+
                              '</div>');

        modelDom.find('.modal-footer .ok-btn').click(function(){
            modelDom.modal('hide');
            return false;
        });

        modelDom.modal({
            'backdrop' : true ,
            'show' : true
        });

        modelDom.bind('hidden' , function(){
            callback();
            modelDom.remove();
        });
    };
})( jQuery , window );
