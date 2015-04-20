/**
 * Created by vikram on 19/1/15.
 */
var app = angular.module('myApp', []);
var BYTE_URL = "https://pipes.yahoo.com/pipes/pipe.run?_id=276d8c6f950f196eeded8c8263002b05&_render=json";
var CITY = "pittsburgh";
app.controller("SearchCtrl", function ($scope, $http) {

    $scope.loading = true;
    $scope.city = CITY;
    query_pipe($http, $scope, CITY);
    $scope.submitForm = function () {
        var search = $("#searchTextField").val();
        search = search.substring(0, search.indexOf(','));
        $scope.city = search;
        console.log(search);
        query_pipe($http, $scope, search);
    }

});

function query_pipe($http, $scope, city) {


    $scope.loading = true;
    $http({
        url: BYTE_URL,
        method: "GET",
        params: {city: city}
    }).
        success(function (data, status, headers, config) {
            // this callback will be called asynchronously
            // when the response is available
            parse_pipe(data, $scope);
            // alert("data");
        }).
        error(function (data, status, headers, config) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.


        });


}

function error_state($scope) {
    alert("Sorry! Try a different city!");
}

function parse_pipe(data, $scope) {
    try {

        //  console.log(data);
        var images_data = data.value.items[1].channel.item;
        var images = [];
        for (var i = 0; i < images_data.length; i++) {
            //  console.log(news_default[i]);
            var news_object = {"image": images_data[i]['media:content'], "thumb": images_data[i]['media:thumbnail'],"link":images_data[i]['link'],"title":images_data[i]['title']};
            images.push(news_object);

        }

        console.log(images_data);

        var weather = data.value.items[0].item;
        weather.condition = weather['yweather:condition'];
        weather.forecast = weather['yweather:forecast'];
        // console.log(weather);

        //  console.log(data.value.items[0]);

        $scope.news = data.value.items[2].channel.item;
        //  console.log(data.value.items[1].channel.item);
        $scope.images = images;
        $scope.weather = weather;
        $scope.loading = false;

    } catch (err) {
        console.log(err);
        error_state($scope);

    }
}


function microappscope() {

    console.log(angular.element($("#body")).scope());
    return angular.element($("#body")).scope();

}

app.filter('weather', function ($sce) {

    return function (val) {

        if (val == undefined)
            return "";

        val = val.substring(0, val.indexOf('<b>Current Conditions:</b>'));

        return $sce.trustAsHtml(val);

    };

});

app.filter('title', function ($sce) {

    return function (val) {
        if (val == undefined)
            return "";

        val = val.replace("Conditions for ", "");

        val = val.substring(0, val.indexOf(','));

        return $sce.trustAsHtml(val);

    };

});

app.filter('clean', function ($sce) {

    return function (val) {

        return $sce.trustAsHtml(val);

    };

});

var autocomplete;
function initialize() {
    var input = document.getElementById('searchTextField');
    var options = {
        types: ['(cities)']
    };

    var autocomplete = new google.maps.places.Autocomplete(input, options);

    google.maps.event.addListener(autocomplete, 'place_changed', function () {
        var place = autocomplete.getPlace();
        //  document.getElementById('lat').value = place.geometry.location.lat();
        //  document.getElementById('lng').value = place.geometry.location.lng();
        console.log("submit");
        angular.element($("#search2")).scope().submitForm();
        //  microappscope().$apply();
        // $("#form-place").submit();
        //alert(place.name);
        // alert(place.address_components[0].long_name);


    });
    var place = autocomplete.getPlace();
    //document.getElementById('search').value = place.name;

}
google.maps.event.addDomListener(window, 'load', initialize);

$(document).ready(function () {


    $('#form-place').bind("keyup keypress", function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            e.preventDefault();
            return false;
        }
    });
});

