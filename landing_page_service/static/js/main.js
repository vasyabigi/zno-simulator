$(document).ready(function () {

    //anchor landing smooth
    $('a[href^="#"]').on('click', function (event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top
            }, 800);
        }
    });

    /*top*/
    $("#toTop").click(function () {
        $("html, body").animate({ scrollTop: 0 }, 800);
    });

    /*btn header hover*/
    // var $btnPr = $('#btn-primary');
    // var $btnSec = $('#btn-secondary');

    // $btnSec.mouseover(function () {
    //     $btnPr.addClass('btn--transparent');
    //     $(this).removeClass('btn--transparent');
    // });

    // $btnSec.mouseout(function () {
    //     $(this).addClass('btn--transparent');
    //     $btnPr.removeClass('btn--transparent');
    // });

    /*mobile header btn*/
    var containerWidth = $("body").width();

    if (containerWidth <= 768) {
        $btnPr.removeClass('btn--big');
        $btnSec.removeClass('btn--big');
    }

});
