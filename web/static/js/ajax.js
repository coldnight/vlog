function VlogAjax(){
    this.type = "POST";
    this.url = "/admin/ajax";
}

var vlog = new VlogAjax()

vlog.get_link_title = function(title, tagid){
    var result = null;
    r = $.ajax({
        type:this.type,
        url : this.url,
        dataType:"json",
        data: {"action": "get_link_title", "title":title},
        success: function(data){
            if (data.status){
                $(tagid).val(data.data);
            }
        }
    });
};

vlog.auto_save = function(data){
};
