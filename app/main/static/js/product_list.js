
let getUrl = '/api/1.0/products/all'
let menUrl = '/api/1.0/products/men'
let womenUrl = '/api/1.0/products/women'
let accUrl = '/api/1.0/products/accessories'
let productsDiv = document.querySelector('#products')
function ajax(src, callback){
    let initialUrl = src;
    let initaialXhr = new XMLHttpRequest();
    initaialXhr.open('GET', initialUrl, true);
    initaialXhr.onload = function() {
    if (initaialXhr.status >= 200 && initaialXhr.status < 400) {
        let data = JSON.parse(initaialXhr.responseText);
        callback(data)
    }
    };
    initaialXhr.send();
} 

function render(data){
    console.log(data)
    let results = data.data
    for (let i = 0; i < results.length; i++){
        let result = results[i]
        let newproduct = document.createElement('div')
        newproduct.classList =`product col-6 col-xl-4`
        newproduct.innerHTML =  `
                <img src='${result.main_image}' class="img-fluid" alt="Responsive image">
                <div class="product-title">${result.title}</div>
                <div class="product-price">${result.price}</div>
        `
        productsDiv.appendChild(newproduct)
    }
   }


if (window.location.href.includes("all")) {
ajax(getUrl, function(response){
         render(response); });
} else if (window.location.href.includes("women")) {
    ajax(womenUrl, function(response){
        render(response); });
} else if (window.location.href.includes("men")) {
    ajax(menUrl, function(response){
        render(response); });
} else if (window.location.href.includes("accessories")) { 
    ajax(accUrl, function(response){
        render(response); });
}

