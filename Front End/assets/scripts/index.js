console.log("hello world")
 // HOST = location.protocol + "//" + location.host;
HOST = "https://benmccormack.xyz/rest";

function login(){
    let username = document.getElementById("username-login").value;
    let password = document.getElementById("password-login").value;

    $.ajax({
        "method": "POST",
        "url":  HOST + "/api/login/",
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json",
        },
        "data": JSON.stringify({
            "username": username,
            "password": password
        })
        }).done(function(data,status,xhr){
            //storing the token returned into local storage
            localStorage.authToken = data.token;
            window.location.href = "map.html";
            
        }).fail(function(){
            alert("incorrect credentials have been entered!");
        });
}

function register(){
    let username = document.getElementById("username-register").value;
    let email = document.getElementById("email-register").value;
    let password = document.getElementById("password-register").value;

    //creating the request
    $.ajax({
        "method":"POST",
        "url":  HOST + "/api/register/",
        "timeout": 0,
        "headers":{
            "Content-Type": "application/json",
        },
        "data": JSON.stringify({
            "username": username,
            "email": email,
            "password": password
        })
    }).done(function(data){
        //if registration ok, we want to redirect user to login page
        // we need to create the miltiple pages on single page first before we do this.
        window.location.href = "index.html";
        alert("Registration Successful! Please Login")
    })
}

function logout(){
    console.log("logout pressed");
    window.localStorage.clear();
    //redirect to the home page
    window.location.href = "index.html";

}

function checkAuthentication(){
    // creating an ajax call to check if the user is authenticated
    // if authenticated return true otherwise send them to the homepage
    $.ajax({
        type: "POST",
        headers: {
            "Authorization": "Token " + localStorage.authToken
        },
        url: HOST + "/api/checkauthentication/",
    }).done(function(data, status, xhr){
        console.log("User token is valid.")
    }).fail(function (xhr,status,error){
        window.location.href = "index.html";
    })
}


// map functions
function update_db(lng, lat){
    let locString = lng + ", " + lat;

    $.ajax({
        type: "POST",
        headers: {
            "Authorization": "Token " + localStorage.authToken
        },
        url: HOST + "/api/updatedb/",
        data: {
            "last_location": locString
        }
    }).done(function(data, status, xhr){
        console.log("Location has been updated in the database.")
    }).fail(function (xhr,status,error){
        console.log("Updating the database has failed!");
    })
}

function favourite(name){
    console.log("clicked")
    console.log(name);
}

if ("serviceWorker" in navigator) {
    window.addEventListener("load", function() {
      navigator.serviceWorker
        .register("/serviceWorker.js")
        .then(res => console.log("service worker registered"))
        .catch(err => console.log("service worker not registered", err))
    })
  }