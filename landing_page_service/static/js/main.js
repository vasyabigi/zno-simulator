$(document).ready(function () {

    //anchor landing smooth
    $('a[href^="#"]').on('click', function (event) {
        console.log("HERE!");

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

    console.log('HAPPY');

});
