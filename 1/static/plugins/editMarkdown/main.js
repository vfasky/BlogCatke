/**
 * Created by PyCharm.
 * User: vfasky
 * Date: 12-2-2
 * Time: 下午2:30
 * To change this template use File | Settings | File Templates.
 */
jQuery(function(){
    var form = window.articleForm;

    // 加入编辑器 & 预览
    var previewBox = jQuery('<div class="article-preview"></div>');
    var converter = new Showdown.converter();

    //扩展编辑器
    var editor = form.dom().find('textarea');
    var QcoreEditWidth = new Qcore.editor( editor );

    // mIu nameSpace to avoid conflict.
    var miu = {
        markdownTitle: function(markItUp, char) {
            heading = '';
            n = $.trim(markItUp.selection||markItUp.placeHolder).length;
            for(i = 0; i < n; i++) {
                heading += char;
            }
            return '\n'+heading;
        }
    }

    var QcoreMarkDownSettings = {
        previewParserPath:	'',
        onShiftEnter:		{keepDefault:false, openWith:'\n\n'},
        markupSet: [
            {name:'First Level Heading', key:'1', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
            {name:'Second Level Heading', key:'2', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
            {name:'Heading 3', key:'3', openWith:'### ', placeHolder:'Your title here...' },
            {name:'Heading 4', key:'4', openWith:'#### ', placeHolder:'Your title here...' },
            {name:'Heading 5', key:'5', openWith:'##### ', placeHolder:'Your title here...' },
            {name:'Heading 6', key:'6', openWith:'###### ', placeHolder:'Your title here...' },
            {separator:'---------------' },
            {name:'粗体', key:'B', openWith:'**', closeWith:'**'},
            {name:'斜体', key:'I', openWith:'_', closeWith:'_'},
            {separator:'---------------' },
            {name:'无序列表', openWith:'- ' },
            {name:'有序列表', openWith:function(markItUp) {
                return markItUp.line+'. ';
            }},
            {separator:'---------------' },
            {name:'图片', key:'P', beforeInsert: QcoreEditWidth.widget['photo'] },
            {name:'连接/附件', key:'L', beforeInsert: QcoreEditWidth.widget['link'] },
            {separator:'---------------'},
            {name:'引用', openWith:'> '},
            {name:'代码', key:'D' , openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'}
        ]
    }

    editor.markItUp(QcoreMarkDownSettings).keyup(function(){
        var data = jQuery(this).val();
        var html = converter.makeHtml( data );
        previewBox.html(html)
    });

    previewBox.appendTo( form.dom().find('.span11') );


})