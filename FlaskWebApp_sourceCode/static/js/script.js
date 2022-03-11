//javascript file for the santa barbara house prediction web application
//This script gets user input (house features) from main HTML
//makes an http request to the local flask app and gets a price prediction
//Then updates the HTML page to display price prediction

//path for flask api
const HOUSE_API="/predict";

//quick function for turning string outputs to floats
function fl(string) {
    return parseFloat(string)
}

//function to assign dummy variables when a commuunity is selected
function communities(community) {
    var IV=0;
    var montecito=0;
    var HR=0;
    
    if (community=='isla vista'){IV=1};
    if (community=='montecito'){montecito=1};
    if (community=='hope ranch'){HR=1};
    
    return [IV, montecito, HR]
}

//Simple function to create dummy variables when a zipcode is selected
function zipcodes(zipcode) {
    var z93067=0;
    var z93101=0;
    var z93103=0;
    var z93105=0;
    var z93108=0;
    var z93109=0;
    var z93110=0;
    var z93111=0;
    var z93117=0;
    

    if (zipcode=='93067'){z93067=1};
    if (zipcode=='93101'){z93101=1};
    if (zipcode=='93103'){z93103=1};
    if (zipcode=='93105'){z93105=1};
    if (zipcode=='93108'){z93108=1};
    if (zipcode=='93109'){z93109=1};
    if (zipcode=='93110'){z93110=1};
    if (zipcode=='93111'){z93111=1};
    if (zipcode=='93117'){z93067=1};

    
    return [ z93067, z93101, z93103, z93105, z93108, z93109, z93110, z93111, z93117]
}




//Function to extract values from the user input on the HTML when the submit button is hit 
function onSubmit() {
    //text boxes
    var beds=d3.select("#beds").property("value");
    var baths=d3.select("#baths").property("value");
    var sqft=d3.select("#sqft").property("value");
    var area=d3.select("#area").property("value");
    var age=d3.select("#age").property("value");
    
    //dropdown menus (yes/no)
    var garage=d3.select("#garage").property("value");
    var fireplace=d3.select("#fireplace").property("value");    
    var ocean=d3.select("#ocean").property("value");    
    var mountain=d3.select("#mountain").property("value");    
    var pool=d3.select("#pool").property("value");
    var upstairs=d3.select("#upstairs").property("value");
    
    //dropdowns that need dummies
    var community=d3.select("#community").property("value");
    var zipcode=d3.select("#zipcode").property("value");
    
    //assign community dummy variables
    [IV, montecito, HR]=communities(community);
    data_in=[IV, montecito, HR];
    
    //assign zipcode dummy variables
    var ziparray=zipcodes(zipcode)
    
    //create the array of input data
    //several variables were normalized and/or scaled in training the model, so the same transformations are applied here:
    var input_data=[fl(beds), Math.log(fl(baths)+1), (Math.log((fl(sqft)/1000)+1)), Math.log(fl(area)+1), fl(age), 
    fl(garage), fl(fireplace), fl(ocean), fl(mountain), HR, montecito, fl(pool), 
    fl(upstairs), IV, 0].concat(ziparray);
    
    //log the transformed input data to the console:
    console.log(input_data);
    
    //call our function that makes a http request to our flask api to get a price prediction
    callPricePredictionAPI(input_data);


}


//Simple function that takes in predicted price and updates our empty HTML element that displays the predicted price
function updatePricePrediction(price) {

    var h1=d3.select('#housePrice');
    
    var housePriceTemplate=`Estimated House Price: <span style= color: white">$ ${price} Million</span>`;

    h1.html(housePriceTemplate)
    
    }

//This function makes an http request to our flask api, sending the user input data and getting a price prediction
function callPricePredictionAPI(value) {

    //Turns our data and our header into a json format
    const HouseData=JSON.stringify({'input':value});
    var headers=JSON.stringify({"Content-Type": "application/json"});
    
    //log ou data to the console
    console.log(HouseData);
    
    //make an http request using fetch to pass in house features to flaskAPI, get prediction, and pass it into our html updating function
    fetch(HOUSE_API, {
      method:"POST",
      body: HouseData,
      headers: {
        "Content-type": "application/json"
      }
        }).then(response => response.json()
        .then(function(data) {
            console.log(data['response']);
            updatePricePrediction(Math.round((Math.exp(data['response'])-1)*100)/100);
            
             }))
            

   
    }
    
//activate the onSubmit function when the button is clicked
d3.select("#button").on("click",onSubmit);







