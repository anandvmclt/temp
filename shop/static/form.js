 function validateForm() {
  var fn = document.forms["myForm"]["name"].value;
  var em = document.forms["myForm"]["email"].value;
  var gd = document.forms["myForm"]["message"].value;
  if (fn == "") {
    alert("Name must be filled out");
    return false;
    }
   else if (em == "") {
    alert("Email must be filled out");
    return false;
    }
   else if (gd == "") {
    alert("Please choose your Gender");
    return false;
    }
}
