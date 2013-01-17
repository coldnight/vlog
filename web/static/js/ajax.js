/*
 * Author   :   cold
 * Email    :   wh_linux@126.com
 * Date     :   16/01/13 14:13
 * Desc     :   与后台交互ajax
 */
function VlogAjax(){
    this.type = "POST";
    this.adminurl = "/admin/ajax";
    this.url = "/vl-ajax";
}

var vlog = new VlogAjax()

/*
 * 获取标题的链接标题
 * @title   标题
 * @tagid   结果放置的标签id
 */
vlog.get_link_title = function(title, tagid){
    var result = null;
    r = $.ajax({
        type:this.type,
        url : this.adminurl,
        dataType:"json",
        data: {"action": "get_link_title", "title":title},
        success: function(data){
            if (data.status){
                $(tagid).val(data.data);
            }
        }
    });
};

