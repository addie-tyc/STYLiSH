// -----------------------------------
let selection = document.querySelector("#selection");
let optionUrl = "/api/1.0/products/recom-parents"
let getUrl = '/api/1.0/products/recom-info?id=' + selection.value;
let selectedDiv = document.querySelector('#selected');
let productsDiv = document.querySelector('#products');

selection.addEventListener('change', function() {
    let selection = document.querySelector("#selection");
    console.log(selection.value)
   });


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

function render_option(data) {
    let results = data.data
    for (let i = 0; i < results.length; i++){
        let result = results[i]
        let newoption = document.createElement('option')
        if (i === 0) {
            newoption.textContent =  "Select A Product"
        } else {
            newoption.value = `${result.item_id}`
            newoption.textContent =  `${result.title}`
        }
        selection.appendChild(newoption)
    }
}

ajax(optionUrl, function(response){
    render_option(response); });


function showRecom() {

    let selection = document.querySelector("#selection");
    let getUrl = '/api/1.0/products/recom-info?id=' + selection.value;
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
        selectedDiv.innerHTML = ""
        productsDiv.innerHTML = ""
        console.log(data)
        let results = data.data
        for (let i = 0; i < results.length; i++){
            let result = results[i]
            let newproduct = document.createElement('div')
            if (i === 0) {
                newproduct.classList =`product selected col-6 col-xl-4`
                newproduct.innerHTML =  `
                        <h1 id=selected>Selected Product</h1>
                        <h2>${result.title}</h2>
                        <h2>Price: ${result.price}</h2>
                        <img src='${result.main_image}' class="img-fluid" alt="Responsive image">`
                        selectedDiv.appendChild(newproduct)
                
            } else {
                newproduct.classList = `product recommended col-6 col-xl-4`
                newproduct.innerHTML = `
                    <h1>Recommended Product</h1>
                    <h2>${result.title}</h2>
                    <h2>Price: ${result.price}</h2>
                    <img src='${result.main_image}' class="img-fluid" alt="Responsive image">`
                    productsDiv.appendChild(newproduct)
            }
            
        }
    }

    ajax(getUrl, function(response){
        render(response); });
}



