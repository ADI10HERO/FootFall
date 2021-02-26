// Hide submenus
$('#body-row .collapse').collapse('hide');

// Collapse/Expand icon
$('#collapse-icon').addClass('fa-angle-double-left');

// Collapse click
$('[data-toggle=sidebar-colapse]').click(function() {
    SidebarCollapse();
});

console.log("loaded")

function SidebarCollapse() {
    $('.menu-collapsed').toggleClass('d-none');
    $('.sidebar-submenu').toggleClass('d-none');
    $('.submenu-icon').toggleClass('d-none');
    $('#sidebar-container').toggleClass('sidebar-expanded sidebar-collapsed');

    // Treating d-flex/d-none on separators with title
    var SeparatorTitle = $('.sidebar-separator-title');
    if (SeparatorTitle.hasClass('d-flex')) {
        SeparatorTitle.removeClass('d-flex');
    } else {
        SeparatorTitle.addClass('d-flex');
    }

    // Collapse/Expand icon
    $('#collapse-icon').toggleClass('fa-angle-double-left fa-angle-double-right');
}

$('.my-item:first').addClass('active-bg');
$('.my-item:first').removeClass('bg-blue');
$('.tab-content:not(:first)').hide();
$('.my-item').click(function(event) {
    event.preventDefault();
    // console.log("shit I got called..")
    var content = $(this).attr('href');
    // console.log($(this))
    $(this).addClass('active-bg');
    $(this).removeClass('bg-blue');

    $(this).siblings().removeClass('active-bg');
    $(this).siblings().addClass('bg-blue');

    $(content).show();
    $(content).siblings('.tab-content').hide();
});