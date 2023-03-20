/* 
* This file defines the JS for the frontend of the app.
* Copyright (C) 2022-2023 Cameron Fairchild 
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

function submitForm(event) {
    $("#result").text("Loading...");
    $.ajax({
        url: '/ping',
        type: 'GET',
        data: $('#form').serialize(),
    }).then((resp) => {
        console.log(resp);
        $('#result').text(JSON.stringify(resp, null, '\t'));
    }).catch((err) => {
        console.log(err);
        resp = err.responseJSON;
        $("#result").text("Failed\n" + JSON.stringify(resp, null, '\t'));
    });

    return false;
}

function submitBalance(event) {
    $("#result-balance").text("Loading...");
    $.ajax({
        url: '/balance',
        type: 'GET',
        data: $('#form-balance').serialize(),
    }).then((resp) => {
        console.log(resp);
        const balance = resp.balance;
        $('#result-balance').text(balance);
    }).catch((err) => {
        console.log(err);
        resp = err.responseText;
        $("#result-balance").text("Failed\n" + resp);
    });
    return false;
}

$(document).ready(function() {
    $('#submit').on('click', submitForm);
    $('#submit-balance').on('click', submitBalance);
});

