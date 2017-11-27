/**
 * Created by zakaria on 2.7.2017.
 */
var newcontainer;

        $.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

        //This is an  ajax call for  create  from the  restfull  API 

     $(function() {
    $('#create-button').bind('click', function() {
    var temp = document.getElementById("cpu");
    var cpu = temp.options[temp.selectedIndex].value;
    var temp2 = document.getElementById("ram");
    var ram = temp2.options[temp2.selectedIndex].value;
    newcontainer = $("#container-name-create").val();

    //alert(cpu);
    //alert(token);
    //alert(ram);
        
      $.getJSON($SCRIPT_ROOT + '/api/create', {

        containername:  $("#container-name-create").val(),
        cpu:cpu,
        ram:ram,
        token: token

      }, function(data) {
        if(data.localeCompare("Nothing") == 0 )
           {
               toastr.error('You choose an existing container name', 'Error!!');
           }

      });
      return false;
    });
  });

    //This ajax   call for  delete from rest API
$(function() {
    $('#delete-button').bind('click', function() {

        
      $.getJSON($SCRIPT_ROOT + '/api/delete', {

        containername:  $("#container-name-delete").val(),
        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });

   //This ajax   call for  start from rest API
$(function() {
    $('#start-button').bind('click', function() {

        
      $.getJSON($SCRIPT_ROOT + '/api/start', {

        containername:  $("#container-name-start").val(),
        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });

  //This ajax   call for  stop from rest API
$(function() {
    $('#stop-button').bind('click', function() {

        
      $.getJSON($SCRIPT_ROOT + '/api/stop', {

        containername:  $("#container-name-stop").val(),
        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });

  //This ajax   call for  info from rest API
/*$(function() {
    $('#info-button').bind('click', function() {

        
      $.getJSON($SCRIPT_ROOT + '/api/infos', {

        containername:  $("#container-name-infos").val(),
        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });*/

$(function() {
    $('#info-button').bind('click', function() {


      $.getJSON($SCRIPT_ROOT + '/api/infos2', {

        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });


 $(function() {
    $('#clone-button').bind('click', function() {


      $.getJSON($SCRIPT_ROOT + '/api/clone', {

        containername:  $("#container-name-clone").val(),
        newcontainername:  $("#new-container-name").val(),
        token: token

      }, function(data) {
        console.log("success")
      });
      return false;
    });
  });


function dollar(id) {
  return document.getElementById(id);
}



var drake = dragula([dollar('drag-elements'), dollar('drop-target')], {
  revertOnSpill: true
});
drake.on('drop', function(el) {
$("#loader-migrate").show();
      $.getJSON($SCRIPT_ROOT + '/api/migrate', {

        //containername:  $("#container-name-to-migrate").val(),
        //destIP:  $("#container-ip-migrate").val(),
        //numIntera:  $("#container-name-nbr").val(),
        containername: newcontainer,
        numIntera: 3,
        destIP: "192.168.122.135",
        token: token


      }, function(data)

      {
        console.log("success")

      });
      return false;



});



//LongPolling


(function poll() {
   setTimeout(function() {
       $.ajax({ url: "/api/result",



        success: function(data) {
      //console.log(data.action)
      //alert(data.token.localeCompare(token))
      //console.log(data.token)
      //console.log(token)

            //temp = data.split("#");
            //if(data.token.localeCompare(token)== 0)
            //alert("test test")
            if(data.token == token)
            {
            //alert("token php :")
      //alert("token DB:"+data.token)

            switch(data.action) {
                     case "create":
                          //console.log( temp[1] )
                          if (data.rsdb == "1")
                          {
                          toastr.success('The container '+ data.containerName +' is  created successfully', 'Create')
                          var  newcontainer = '<div id="container21" class="item" ><img class="ui avatar image" src="static/images/container.png"><div class="content"> <p id = "newcontainer">' + data.containerName +'</p> </div></div>'
                          var element = document.getElementById("drag-elements").innerHTML = newcontainer;
                          }
                          else if (data.rsdb=="2")
                          {
                          toastr.error('The container '+ data.containerName +' is  already existing', 'Exist')

                          }
                          else
                          {
                          toastr.error('The container '+ data.containerName +' is  not successfully created', 'Not Create')
                          }
                          break;
                     case "delete":
                           if ( data.rsdb == "1")
                          {
                          toastr.error('The container '+ data.containerName +' is  deleted successfully', 'Delete')
                          }
                          else if (data.rsdb =="2")
                          {
                          toastr.error('The container '+ data.containerName +' doesn\'t exist', 'Exist')

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName +' is  not successfully deleted', 'Not Delete')
                          }
                          break;
                     case "start":
                          if (data.rsdb == "1")
                          {
                          toastr.success('The container '+ data.containerName +' is  started successfully', 'Start')
                          }
                          else if (data.rsdb=="2")
                          {
                          toastr.error('The container '+ data.containerName +' doesn\'t exist to Start it', 'Exist')

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName  +' is  not successfully started', 'Not Start')
                          }
                          break;

                     case "stop":
                          if (data.rsdb == "1")
                          {
                          toastr.warning('The container '+ data.containerName +' is  stopped successfully', 'Stop')
                          }
                          else if (data.rsdb=="2")
                          {
                          toastr.error('The container '+ data.containerName +' doesn\'t exist to Stop it', 'Exist')

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName +' is  not successfully stopped', 'Not Stopped')
                          }
                          break;

                     case "clone":
                          if (data.rsdb == "1")
                          {
                          if (data.newcontainerName == 'None')
                          {

                          }
                          else
                          {
                          toastr.success('The container '+ data.containerName +' is  cloned successfully into ' + data.newcontainerName, 'Clone')
                          }
                          }
                          else if (data.rsdb=="2")
                          {
                          toastr.error('The container '+ data.containerName +' doesn\'t exist to Clone it', 'Exist')

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName +' is  not successfully cloned', 'Not Cloned')
                          }

                          break;
                     case "migrate":
                          if (data.rsdb == "1")
                          {

                          toastr.success('The container '+ data.containerName +' is  migrated successfully', 'Migrate');
                          $("#loader-migrate").hide();
                          }
                           else if (data.rsdb =="2")
                          {
                          toastr.error('The container '+ data.containerName +' doesn\'t exist to Migrate it', 'Exist');
                          $("#loader-migrate").hide();


                          }
                           else if (data.rsdb =="10")
                          {
                          toastr.error('The container '+ data.containerName +'  has the same name in the remote host', 'Exist');
                          $("#loader-migrate").hide();

                          }
                           else if (data.rsdb =="8")
                          {
                          toastr.error('There is no enough resources for the container '+ data.containerName , 'Resources');
                          $("#loader-migrate").hide();

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName +' is  not successfully migrated', 'Not Migrate');
                           $("#loader-migrate").hide();
                          }
                          break;
                     case "getinfo":
                          if (data.rsdb == "1")
                          {
                          if(data.State == 'RUNNING')
                          {
                          alert(' Name : '+ data.containerName +'\n State : '+ data.State +'\n PID : '+ data.PID + '\n IP : '+ data.IP + '\n CPU use : ' + data.CPU + '\n BlkIO use : ' + data.BlkIO + '\n Memory use : '+ data.Memory + '\n Link : ' + data.Link + '\n TX bytes : ' + data.TXbytes +'\n RX bytes : '+ data.RXbytes, 'Getinfo')
                          }
                          else
                          {
                          alert(' Name : '+ data.containerName +'\n State : '+ data.State, 'Getinfo')

                          }
                          }
                          else if(data.rsdb == "2")
                          {
                           toastr.error('The container '+ data.containerName +' doesn\'t exist to get the information', 'Exist')

                          }
                          else
                          {
                           toastr.error('The container '+ data.containerName +' is  not successfully getting informations', 'Not Getinfo')

                          }


                          break;




                         
}}

       }, dataType: "json", complete: poll });
    }, 5000);
})();