var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var panel = this.nextElementSibling;
        if (panel.style.maxHeight){
            panel.style.maxHeight = null;
        } else {
            panel.style.maxHeight = panel.scrollHeight + "px";
        }
    });
}

const btnNumlike = document.querySelectorAll('.section-product-page-top-block');
const tablike = document.querySelectorAll('.section-product-page-content')

btnNumlike.forEach(function (item){
    item.addEventListener('click', function (){
        btnNumlike.forEach(function (i){
            i.classList.remove('section-product-page-top-block-active')
        })

        item.classList.add('section-product-page-top-block-active')

        let tubIDlike = item.getAttribute('data-tab');
        let tabActivelike = document.querySelector(tubIDlike);

        tablike.forEach(function (item){
            item.classList.remove('section-product-page-content-active')
        })
        tabActivelike.classList.add('section-product-page-content-active')

    })
})



const btnNumlike2 = document.querySelectorAll('.section-lk-container-right-top-block');
const tablike2 = document.querySelectorAll('.section-lk-container-content')

btnNumlike2.forEach(function (item){
    item.addEventListener('click', function (){
        btnNumlike2.forEach(function (i){
            i.classList.remove('section-lk-container-right-top-block-active')
        })

        item.classList.add('section-lk-container-right-top-block-active')

        let tubIDlike = item.getAttribute('data-tab-lk');
        let tabActivelike = document.querySelector(tubIDlike);

        tablike2.forEach(function (item){
            item.classList.remove('section-lk-container-content-active')
        })
        tabActivelike.classList.add('section-lk-container-content-active')

    })
})