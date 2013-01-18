$("#note_content").keyup(function(){
    var content = this.value;
    var length = content.length;
    if (length <= 200 ){
        $("#num").text(length);
    } else{
        $("#num").html("<font color='red'>" + length + "</font>")
    }
});

$("#submit").click(function(){
    var content = $("#note_content").val();
    var length = content.length;

    if (length <= 200){
        $("num").text(length);
        $.ajax({
            type:"POST",
            url:"/admin/addnote",
            dataType:"json",
            data:{"content":content},
            success: function(data){
                if (data.status){
                    window.location.reload();
                } else {
                    alert("失败");
                }
            }
        });
    } else {
        alert("超过长度");
    }
});
