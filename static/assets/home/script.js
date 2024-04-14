document.addEventListener("DOMContentLoaded", function () {
    const accordionItems = document.querySelectorAll(".accordion-item");
    accordionItems.forEach((item) => {
        const title = item.querySelector(".accordion-title");
        const content = item.querySelector(".accordion-content");

        title.addEventListener("click", function () {
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                title.classList.remove("show");
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
                title.classList.add("show");
            }
            accordionItems.forEach((otherItem) => {
                if (otherItem !== item) {
                    const otherContent = otherItem.querySelector(".accordion-content");
                    otherContent.style.maxHeight = null;
                    otherItem.querySelector(".accordion-title").classList.remove("show"); // Убираем класс "show" у остальных
                }
            });
        });
    });
});

if (document.querySelector('.w-services')) {
    $('.w-services .wrap_slider .box').click((e) => {
        let target = $(e.target)
        let father_index = $(target).closest('.box').index()
        $('.w-services .wrap_slider .box').removeClass('active');
        $(target).closest('.box').addClass('active');

        $('.w-services .g-l .box').addClass("hidden")
        let el = $('.w-services .g-l').children()[father_index]
        $(el).removeClass("hidden")
    })
}
