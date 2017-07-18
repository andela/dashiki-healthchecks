$(function(){
let $parent = $('#edit-faq__modal .modal-body');
$('.btn-faq__edit').click(function(){
  let $uri = $(this).attr('uri');
  $.ajax({
    url:$uri,
    type:'get',
    success:function($data){
      $parent.html($data);
      CKEDITOR.config.width="100%";
      CKEDITOR.config.toolbar = [
      ['Styles','Format','Font','FontSize','Bold','Italic','Underline','StrikeThrough','-','Undo','Redo',
      'NumberedList','BulletedList','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock']
      ];
      CKEDITOR.replace("id_body",{
        width:['820px']
      });
      $('#edit-faq__modal').modal('show');
    }
  });
});
})

$(function(){
let $parent = $('#edit-cat__modal .modal-body');
$('.btn-cat__edit').click(function(){
  let $uri = $(this).attr('uri');
  $.ajax({
    url:$uri,
    type:'get',
    success:function($data){
      $parent.html($data);
      $('#edit-cat__modal').modal('show');
      }
    });
  });
})
