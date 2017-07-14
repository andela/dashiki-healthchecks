$(function() {

    $(".member-remove").click(function() {
        var $this = $(this);

        $("#rtm-email").text($this.data("email"));
        $("#remove-team-member-email").val($this.data("email"));
        $('#remove-team-member-modal').modal("show");

        return false;
    });

});

$(function(){
let $parent = $('#assign-checks-modal .modal-body');
 $('.assign-check').click(function(){
 var $this = $(this);
 let $uri = $(this).attr('uri');
   $.ajax({
     url:$uri,
     type:'get',
     success:function($data){
       $parent.html($data);
       $("#member-email").val($this.data("email"));
       $('#assign-checks-modal').modal('show');
       }
     });
   });
 })

$(function($) {
    $('.js-multiselect').multiselect({
        right: '#js_multiselect_to_1',
        rightAll: '#js_right_All_1',
        rightSelected: '#js_right_Selected_1',
        leftSelected: '#js_left_Selected_1',
        leftAll: '#js_left_All_1'
    });
});
