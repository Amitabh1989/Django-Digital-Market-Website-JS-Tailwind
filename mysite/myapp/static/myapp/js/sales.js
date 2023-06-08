// Get the data from html file
console.log("I havebeen called")
var daySum = document.getElementsByClassName("day-sum");
var saleDate = document.getElementsByClassName("sale-date");

var sales_val = [];
var date_val = [];
for(var i = 0; i < daySum.length; i++) {
    sales_val.push(parseInt(daySum[i].innerText.replace("$", "")));
    date_val.push(saleDate[i].innerText);
}

console.log("Values : " + sales_val);
console.log("Dates  : " + date_val);


// Chart the sales by date now
const ctx = document.getElementById('myChart');

new Chart(ctx, {
type: 'line',  // other option line, et
data: {
    labels: date_val,
    datasets: [{
    label: 'Last 30 Day Sales',
    data: sales_val,
    borderWidth: 1
    }]
},
options: {
    scales: {
    y: {
        beginAtZero: true
    }
    }
}
});


/* GET PRODUCT DATA HERE */

var prodName = document.getElementsByClassName("prod-name")
var prodSales = document.getElementsByClassName("prod-sales")
let delayed = false; // Add this variable declaration

var pName = [];
var pSales = [];

for(var i = 0; i < prodName.length; i++) {
    pName.push(prodName[i].innerText);
    pSales.push(parseInt(prodSales[i].innerText));
}


// Chart the Product details
const product = document.getElementById('myProductChart');

new Chart(product, {
type: 'bar',  // other option line, et
data: {
    labels: pName,
    datasets: [{
    label: 'Products by Sales',
    data: pSales,
    borderWidth: 1
    }]
},
options: {
    scales: {
    y: {
        beginAtZero: true
    }
    },
    animation: {
        onComplete: () => {
          delayed = true;
        },
        delay: (context) => {
          let delay = 0;
          if (context.type === 'data' && context.mode === 'default' && !delayed) {
            delay = context.dataIndex * 300 + context.datasetIndex * 100;
          }
          return delay;
        },
      }}
});


