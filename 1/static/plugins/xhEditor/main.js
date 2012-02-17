/**
 * Created by PyCharm.
 * User: vfasky
 * Date: 12-2-7
 * Time: 下午7:57
 * To change this template use File | Settings | File Templates.
 */
jQuery(function(){
    var form = window.articleForm;
    var editor = form.dom().find('textarea');

    editor.xheditor({
        skin:'nostyle'
    });

})