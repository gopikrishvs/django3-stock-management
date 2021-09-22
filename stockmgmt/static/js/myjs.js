$(document).ready(function(){

    NProgress.start();
    NProgress.done();
 
    $('.table').paging({limit:6});

    $(".datetimeinput").datepicker({changeYear: true,changeMonth: true, dateFormat: 'yy-mm-dd'});
  });
  