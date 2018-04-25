$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#prod_id").val(res.prod_id);
        $("#prod_name").val(res.prod_name);
        $("#new_qty").val(res.new_qty);
        $("#used_qty").val(res.used_qty);
        $("#open_boxed_qty").val(res.open_boxed_qty);
        $("#restock_level").val(res.restock_level);
        $("#restock_amt").val(res.restock_amt);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#prod_id").val("");
        $("#prod_name").val("");
        $("#new_qty").val("");
        $("#used_qty").val("");
        $("#open_boxed_qty").val("");
        $("#restock_level").val("");
        $("#restock_amt").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // clean out empty properties in data
    function remove_empty(data) {
        for (var propName in data) {
            if (data[propName] === "") {
                delete data[propName]
            }
        }
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {
        var prod_id = $("#prod_id").val();
        var prod_name = $("#prod_name").val();
        var new_qty = $("#new_qty").val();
        var used_qty = $("#used_qty").val();
        var open_boxed_qty = $("#open_boxed_qty").val();
        var restock_level = $("#restock_level").val();
        var restock_amt = $("#restock_amt").val();

        var data = {
            "prod_id": prod_id,
            "prod_name": prod_name,
            "new_qty": new_qty,
            "used_qty": used_qty,
            "open_boxed_qty": open_boxed_qty,
            "restock_level": restock_level,
            "restock_amt": restock_amt,
        };

        remove_empty(data)

        var ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        var prod_id = $("#prod_id").val();
        var prod_name = $("#prod_name").val();
        var new_qty = $("#new_qty").val();
        var used_qty = $("#used_qty").val();
        var open_boxed_qty = $("#open_boxed_qty").val();
        var restock_level = $("#restock_level").val();
        var restock_amt = $("#restock_amt").val();

        var data = {
            "prod_name": prod_name,
            "new_qty": new_qty,
            "used_qty": used_qty,
            "open_boxed_qty": open_boxed_qty,
            "restock_level": restock_level,
            "restock_amt": restock_amt,
        };

        remove_empty(data)

        var ajax = $.ajax({
                type: "PUT",
                url: "/inventory/" + prod_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        var prod_id = $("#prod_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + prod_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        var prod_id = $("#prod_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/inventory/" + prod_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product with ID [" + res.prod_id + "] has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#prod_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {
        var searchKey = $("#searchKey").val();
        var searchValue = $("#searchValue").val();
        var queryString = searchKey + "=" + searchValue

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            var table = '<table class="table-striped">'
            var header = '<thead> <tr>'
            header += '<th class="col-md-1">ID</th>'
            header += '<th class="col-md-2">Product Name</th>'
            header += '<th class="col-md-2">New Qty</th>'
            header += '<th class="col-md-2">Used Qty</th>'
            header += '<th class="col-md-2">Open-boxed Qty</th>'
            header += '<th class="col-md-1">Restock Level</th>'
            header += '<th class="col-md-1">Restock Amount</th>'
            header += '</tr> </thead>'
            table += header
            table += "<tbody>"
            for(var i = 0; i < res.length; i++) {
                entry = res[i];
                var row = "<tr><td>" + entry.prod_id + "</td><td>"
                                     + entry.prod_name + "</td><td>"
                                     + entry.new_qty + "</td><td>"
                                     + entry.used_qty + "</td><td>"
                                     + entry.open_boxed_qty + "</td><td>"
                                     + entry.restock_level + "</td><td>"
                                     + entry.restock_amt + "</td></tr>";
                table += row
            }

            table += "</tbody></table>";
            $("#search_results").append(table);
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
