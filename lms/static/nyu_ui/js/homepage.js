$(function () {
    let $root = $('html, body');
    $('a[href="#course-main"]').click(function () {
        $root.animate({
            scrollTop: $("#course-main").offset().top
        }, 500);
        // setTimeout(function () {
        //     var id = $(".tab .active").attr('class').split(" ")[0];
        //     switchAnimation(id);
        // }, 100);

        return false;
    });

    $(window).scroll(function (e) {
        let scrollTop = $(this).scrollTop();
        let $flag_obj = $('.courses-content');
        let flag = $flag_obj.hasClass("animated");
        if (scrollTop <= 51 && !flag) {
            $flag_obj.addClass("animated");
        }
        if (scrollTop > 51 && flag) {
            $flag_obj.removeClass("animated");
            setTimeout(function () {
                var id = $(".tab .active").attr('class').split(" ")[0];
                switchAnimation(id);
            }, 100);
        }
    });

    typeWriter('span.niuke');
    typeWriter('span.opencourse');
    typeWriter('span.nyushanghai');

    let Accordion = function (el, multiple) {
        this.el = el || {};
        this.multiple = multiple || false;
        let links = this.el.find('.link');
        links.on('click', {el: this.el, multiple: this.multiple}, this.dropdown)
    };

    Accordion.prototype.dropdown = function (e) {
        let $el = e.data.el;
        $this = $(this), $next = $this.next();
        $next.slideToggle();
        $this.parent().toggleClass('open');
        if (!e.data.multiple) {
            $el.find('.submenu').not($next).slideUp().parent().removeClass('open');
        }
    };

    new Accordion($('#accordion'), false);

    $(window).scroll(function () {
        let width = $(window).width();
        if (width < 753) {
            return;
        } else {
            let scrollTop = $(this).scrollTop();
            let height = $(window).height();
            let third = $('.wrapper-about').height();
            let $flag_obj = $('.about-centent');
            let ext = (third - $flag_obj.height()) / 2;
            let flag = $flag_obj.hasClass("animated");
            let lst = [$('.slogan'), $('.sub-slogan'), $('.way-to'), $('.our-qr-code')];

            if (scrollTop <= height + ext && !flag) {
                $flag_obj.addClass("animated");
                $.each(lst, function (index, item) {
                    item.hide();
                });
            }
            if (scrollTop > height + ext && flag) {
                $flag_obj.removeClass("animated");
                setTimeout(function () {
                    var delay = 0;
                    $.each(lst, function (index, item) {
                        setTimeout(function () {
                            item.fadeIn(1000);
                        }, index * delay);
                    });
                }, 200);
            }
        }
    });

    let submenu = $(".course-nav-xs");

    // Fix the location of the course navigation bar
    $(window).scroll(function () {
        let width = $(window).width();
        if (width > 768) {
            return;
        } else {
            let targetTop = $(this).scrollTop();
            let height = $(window).height();
            let heightWhole = $(document).height();
            let footer = $(".visible-xs>.footer-custom").height();
            let third = $(".wrapper-about-xs").height();

            if (height < targetTop && targetTop < heightWhole - footer - third) {
                submenu.css('top', '0');
                submenu.css('position', 'fixed');
                submenu.css('width', '100%');
                submenu.css('z-index', '2');
                submenu.css('opacity', '1');
            } else if (targetTop <= height) {
                submenu.css('top', 'auto');
                submenu.css('position', 'inherit');
                submenu.css('z-index', '2');
                submenu.css('opacity', '1');
            } else {
                submenu.css('top', '0');
                submenu.css('position', 'fixed');
                submenu.css('width', '100%');
                submenu.css('z-index', '-1');
                submenu.css('opacity', '0');
            }
        }

    });

    //Large screen menu click
    $(".tab").click(function () {
        const id = $(this).find("a").attr("class").split(" ")[0];
        menu_tab($(this), id);

        setTimeout(() => {
            $.each($(".submenu").find("a"), (index, item) => {
                if ($(item).attr("class").split(" ")[0] == id) {
                    menu_submenu($(item), id);
                }
            });

        }, 100);
    });

    //Small screen menu click
    $(".submenu").find("a").click(function () {
        const id = $(this).attr("class");
        menu_submenu($(this), id);

        setTimeout(() => {
            $.each($(".tab").find("a"), (index, item) => {
                if ($(item).attr("class").split(" ")[0] == id) {
                    menu_tab($(item).parent(), id);
                }
            });
        }, 100);
    });

    $("a.search-button").click(function () {
        $(".course-search").toggleClass("active")
        $(".search-input").focus();
    });

    $(".search-input").bind("blur", function() {

        setTimeout(() => {
            $(".course-search").removeClass("active");
        }, 300);
    });

    //Large screen menu switching
    // function menu_tab(el, id) {
    //     $(".ul-active").hide();
    //     $(".ul-active").removeClass("ul-active");
    //     $(".course-"+id).toggleClass("ul-active");
    //     $(".course-"+id).slideDown(600);
    //     // $(".course-"+id).show();
    //     $(".tab .active").removeClass("active");
    //     el.find("a").toggleClass("active");
    // }
    //

    function menu_tab(el, id) {
        if ($(".ul-active").hasClass("course-" + id)) {
            return;
        }
        switchAnimation(id);
        $(".tab .active").removeClass("active");
        el.find("a").toggleClass("active");
    }

    function switchAnimation(id) {
        $(".ul-active").hide();
        $(".ul-active").removeClass("ul-active");
        $(".course-" + id).toggleClass("ul-active");
        $(".course-" + id).show();
        $(".course-" + id).find(".grid").hide();
        var delay = 200;
        $.each($(".course-" + id).find(".grid"), function (index, item) {
            setTimeout(function () {
                $(item).slideDown(500);
            }, index < 10 ? index * delay : 10 * delay);
        });
    }

    //Small screen menu switching
    function menu_submenu(el, id) {
        $(".course-pick").text(el.text());
        $(".submenu").hide();
        $(".open").toggleClass("open");
        $(".ul-xs-active").hide();
        $(".ul-xs-active").removeClass("ul-xs-active");
        $(".course-xs-" + id).toggleClass("ul-xs-active");
        $(".submenu .active").removeClass("active");
        el.find("a").toggleClass("active");
        let width = $(window).width();
        if (width > 768) {
            return;
        } else {
            $root.animate({
                scrollTop: $("#course-main").offset().top
            }, 500);
        }

    }

});

// Title animation
function typeWriter(el) {
    // Our selector
    var $copy = $(el);

    // Use lettering.js to wrap each character & word in a span tag
    $copy.lettering();

    // Our declations
    var $span = $("span");
    var length = $span.length;
    var array = [];

    // Push reference to our array
    for (var i = 1; i <= length; i++)
        array.push(i);

    // Randomise array
    shuffleArray(array);

    // Wrap each word in its own div so words don't split on line break
    $copy.wrapInner('<span class="word"></span>');
    var regEx = new RegExp(/<span class=\"char(\d+)\"> <\/span>/g);
    $copy.html($copy.html().replace(regEx, '</span><span class="word">'));

    // Fire first animation
    setTimeout(function () {
        animateLetters(array, length, true);
    }, 800);
}

// Animate the letters
function animateLetters(array, length, animIn) {
    // Scale in or out?
    var scale = (animIn) ? 1 : 1.5;

    // Arrange array ordering
    var arrayToUse = (animIn) ? array : array.reverse();

    // Opacity value to use
    var opacity = (animIn) ? 1 : 0;

    var time = 20;

    // Loop through each letter, adding inline styles
    for (var i = 0; i <= length; i++) {
        $(".char" + arrayToUse[i]).attr("style", "opacity: " + opacity + "; transition-delay: " + (time * i) + "ms; transform:perspective(1050px) rotateY(0deg) scale(" + scale + "); -webkit-transition-delay: " + (time * i) + "ms; -webkit-transform:perspective(1050px) rotateY(0deg) scale(" + scale + ");");
    }

    // Flip animIn value for next animation
    // animIn = (animIn) ? false : true;

    // Randomise array for next animate in
    // array = (animIn) ? shuffleArray(array) : array;

    // How long before refiring?
    // var timeout = (animIn) ? 3500 : 5000;

    // Animate out or show replay button

    /*
   setTimeout(function() {
      if (!animIn) {
          // Animate out
          animateLetters(array, length, animIn);
      } else {
          // Create replay button
          $("body").prepend('<button>Replay?</button>');
          $("button").on("click", function() {
              $(this).remove();
              // Replay animation
              setTimeout(function() {
                  animateLetters(array, length, true);
              }, 500);

          });
      }
  }, timeout);
    */

}

// Randomize array element order in-place. Using Fisher-Yates shuffle algorithm.
// Ref: http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}

(function ($) {

    var default_setting = {
        subject: 'Default',
        cardw: 370,
        cardh: '100%',
        margin: 0,
        moven: 1,
    };

    function effect() {
        var target = this;
        // target.find('.slide-wrap').hover(function () {
        //     target.find('.shift').addClass('shift-active');
        //     target.find('i').addClass('i-active');
        // }, function () {
        //     target.find('.shift').removeClass('shift-active');
        //     target.find('i').removeClass('i-active');
        // });

        target.find('.right').hover(function () {
            target.find('.slide').addClass('slide-active-r');
        }, function () {
            target.find('.slide').removeClass('slide-active-r');
        });

        target.find('.left').hover(function () {
            target.find('.slide').addClass('slide-active-l');
        }, function () {
            target.find('.slide').removeClass('slide-active-l');
        });

        target.find('.shift').hover(function () {
            target.find('i').addClass('i-active-move');
        }, function () {
            target.find('i').removeClass('i-active-move');
        });
    }

    function init(cus_setting) {
        // overwrite setting
        var init_setting = $.extend({}, default_setting, cus_setting || {});
        var slidewraph = init_setting.cardh;
        var covered = init_setting.cardw - 33	//coverd part of card (at both tails of box).
        if (init_setting.cardn == '100%') {
            var boxw = init_setting.cardn;
        } else {
            var boxw = init_setting.cardw * init_setting.cardn + init_setting.margin * (init_setting.cardn - 1) - covered * 2; //box width 845
        }
        var singlemove = (init_setting.cardw + init_setting.margin) * init_setting.moven;	//transform distance .
        var listn = this.find('li').length - 2;
        var boundary = (init_setting.cardw + init_setting.margin) * (listn) - singlemove;
        var target = this;
        target.find('.slide-wrap').height(slidewraph);
        target.find('ul').css({left: -covered});
        target.find('li').css("margin-right", init_setting.margin);
        target.find('li:not(.first,.last)').width(init_setting.cardw);
        target.find('li.first').css('margin-right', 40);
        target.find('li').height(init_setting.cardh);
        target.find('.course-item').width(init_setting.cardw);
        target.find('.course-item').height(init_setting.cardh);

        effect.call(target);
        var movement = 0;
        target.find('.right').click(function (event) {
            var now = Math.floor($(window).width() / singlemove - 1) * singlemove;
            if (Math.abs(movement) + now < boundary) {
                movement -= singlemove;
            }
            target.find('ul').hover().css('transform', 'translateX(' + movement + 'px)');
        });

        target.find('.left').click(function (event) {
                if (movement < 0) {
                    movement += singlemove;
                }
                target.find('ul').hover().css('transform', 'translateX(' + movement + 'px)');
            }
        );

        target.find('.right').mousedown(function (e) {
            if (e.which == 1) {
                var stop;
                stop = setInterval(function () {
                    target.find('.right').click();
                }, 200);

                target.find('.right').mouseup(function () {
                    clearTimeout(stop);
                });
            }
        });

        target.find('.left').mousedown(function (e) {
            if (e.which == 1) {
                var stop;
                stop = setInterval(function () {
                    target.find('.left').click();
                }, 200);

                target.find('.left').mouseup(function () {
                    clearTimeout(stop);
                });
            }
        });

        $(window).resizeEnd(function (e) {
            if (target.find('li').width() >= singlemove) {
                var now = Math.floor($(window).width() / singlemove - 1) * singlemove;
                if (Math.abs(movement) + now > boundary) {
                    movement = -(boundary - now);
                    target.find('ul').hover().css('transform', 'translateX(' + movement + 'px)');
                }
            }

        }, 300);
    }

    $.fn.slider = function (setting) {
        if (setting && typeof setting === 'object') {
            init.call(this, setting);
        } else if (!setting) {
            init.call(this);
        }
    };


    $.fn.resizeEnd = function (callback, timeout) {
        $(this).resize(function () {
            var $this = $(this);
            if ($this.data('resizeTimeout')) {
                clearTimeout($this.data('resizeTimeout'));
            }
            $this.data('resizeTimeout', setTimeout(callback, timeout));
        });
    };
})(jQuery);
