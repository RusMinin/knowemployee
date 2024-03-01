// После изменения кода обфускацию проводить тут https://obfuscator.io/

function getParameterByName(name, url = window.location.href) {
    name = name.replace(/[\[\]]/g, '\\$&');
    let regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

let encodedErr = getParameterByName('e');

if (encodedErr && encodedErr.trim() !== "") {
    let decodedErr = atob(encodedErr);
    let newURL = window.location.protocol + "//" + window.location.host + window.location.pathname;
    history.replaceState({}, '', newURL);

    alertErr(decodedErr)
}

function alertErr(text){
    let html = `
    <div class="alert-err">
        <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 2c5.523 0 10 4.478 10 10s-4.477 10-10 10S2 17.522 2 12 6.477 2 12 2Zm0 1.667c-4.595 0-8.333 3.738-8.333 8.333 0 4.595 3.738 8.333 8.333 8.333 4.595 0 8.333-3.738 8.333-8.333 0-4.595-3.738-8.333-8.333-8.333Zm-.001 10.835a.999.999 0 1 1 0 1.998.999.999 0 0 1 0-1.998ZM11.994 7a.75.75 0 0 1 .744.648l.007.101.004 4.502a.75.75 0 0 1-1.493.103l-.007-.102-.004-4.501a.75.75 0 0 1 .75-.751Z" fill="#ffffff" class="fill-212121"></path></svg>
        <p>${text}</p>
        <button class="closeAler">
            <svg viewBox="0 0 24 24" xml:space="preserve" xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24"><path d="M5.3 18.7c.2.2.4.3.7.3s.5-.1.7-.3l5.3-5.3 5.3 5.3c.2.2.5.3.7.3s.5-.1.7-.3c.4-.4.4-1 0-1.4L13.4 12l5.3-5.3c.4-.4.4-1 0-1.4s-1-.4-1.4 0L12 10.6 6.7 5.3c-.4-.4-1-.4-1.4 0s-.4 1 0 1.4l5.3 5.3-5.3 5.3c-.4.4-.4 1 0 1.4z" id="_icons" fill="#ffffff" class="fill-000000"></path></svg>
        </button>
    </div>
    `;
    $('.wrapper').append(html)
    $('.alert-err').css('top', "-100px")

    setTimeout(()=>{
        $('.alert-err').css('transition', "0.4s ease")
        $('.alert-err').css('top', "20px")
    }, 500)

    setTimeout(()=>{
        $('.alert-err').css('transition', "0.4s ease")
        $('.alert-err').css('top', "-100px")

        setTimeout(()=>{
            $('.alert-err').remove()
        }, 500)
    }, 3000)

    $('.closeAler').click(()=>{
        $('.alert-err').css('transition', "0.4s ease")
        $('.alert-err').css('top', "-100px")

        setTimeout(()=>{
            $('.alert-err').remove()
        }, 500)
    })
}

$(document).ready(function() {
    const selectCountries = $('#countries');

    $.ajax({
        url: './static/assets/country.json',
        type: 'GET',
        dataType: 'json'
    }).done(function(data) {
        data.forEach(function(country) {
            const countryCode = country.data.code.toLowerCase();
            const countryName = country.data.name_country[0].name;
            const isSelected = countryName === "Canada";  // Проверяем, является ли страна Канадой
            const option = new Option(countryName, countryCode, isSelected, isSelected);
            selectCountries.append(option);
        });

        selectCountries.select2({
            templateResult: formatCountry,
            templateSelection: formatCountry
        });

        selectCountries.val('ca').trigger('change');
    });
});

function formatCountry(country) {
    if (!country.id) { return country.text; }
    const baseUrl = "./static/assets/images/flags/";
    url = baseUrl + country.id.toLowerCase() + ".png"
    const $country = $(
        `<span><img src="${url}" alt="${country.text}"/>` + country.text + '</span>'
    );
    return $country;
};


$('.pass-hide').click((e) => {
    let target = $(e.currentTarget);
    let father = target.closest('.pass');
    let allPassHides = father.find('.pass-hide');
    let index = allPassHides.index(target);

    if (index == 0) {
        father.find('input').attr('type', 'text');
        $(allPassHides[0]).addClass('hidden'); 
        $(allPassHides[1]).removeClass('hidden');
    } else if (index == 1) {
        father.find('input').attr('type', 'password');
        $(allPassHides[1]).addClass('hidden');
        $(allPassHides[0]).removeClass('hidden');
    }
});

function resetPasswordFields() {
    $('.pass').each(function() {
        let father = $(this);
        let allPassHides = father.find('.pass-hide');
        father.find('input').attr('type', 'password');
        $(allPassHides[0]).removeClass('hidden');
        $(allPassHides[1]).addClass('hidden');
    });
}

function validator(alert=true){
    let count = 0;
    // Company
    if(document.querySelector('#company')){
        if($('#company').val() == "" || $('#company').val().split("").length > 40){
            if($('#company').val() == ""){
                if ($('#acceptTerms').prop('checked') || alert == true){
                    $('#company').closest('.alr').find(".alr-t").text("* The company name field is empty")
                    $('#company').addClass("invalid")
                }
            }
            if($('#company').val().split("").length > 40){
                if ($('#acceptTerms').prop('checked') || alert == true){
                    $('#company').closest('.alr').find(".alr-t").text("* The company name is too long, please shorten it")
                    $('#company').addClass("invalid")
                }
            }
        }else{
            $('#company').removeClass("invalid")
            $('#company').closest('.alr').find(".alr-t").text("")
            count++;
        }
    }
    

    // Email
    let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if($('#email').val() == "" || $('#email').val().split("").length > 40 || !emailPattern.test($('#email').val())){
        if($('#email').val() == ""){
            if ($('#acceptTerms').prop('checked') || alert == true){
                $('#email').closest('.alr').find(".alr-t").text("* The email field cannot be empty")
                $('#email').addClass("invalid")
            }
        }
        if($('#email').val().split("").length > 40){
            if ($('#acceptTerms').prop('checked') || alert == true){
                $('#email').closest('.alr').find(".alr-t").text("* Email is too big, more than 40 characters")
                $('#email').addClass("invalid")
            }
        }

        if (!emailPattern.test($('#email').val())){
            if ($('#acceptTerms').prop('checked') || alert == true){
                $('#email').closest('.alr').find(".alr-t").text("* The e-mail is not up to standard.")
                $('#email').addClass("invalid")
            }
        }
    }else{
        $('#email').removeClass("invalid")
        $('#email').closest('.alr').find(".alr-t").text("")
        count++;
    }

    // Password
    if($('#password').val() == "" || $('#password').val().split("").length < 10){
        if($('#password').val() == ""){
            if ($('#acceptTerms').prop('checked') || alert == true){
                $('#password').closest('.alr').find(".alr-t").text("* The password cannot be empty")
                $('#password').addClass("invalid")
            }
        }else{
            if($('#password').val().split("").length < 10){
                if ($('#acceptTerms').prop('checked') || alert == true){
                    $('#password').closest('.alr').find(".alr-t").text("* Password must not be less than 10 characters")
                    $('#password').addClass("invalid")
                }
            }
        }
        
    }else{
        $('#password').removeClass("invalid")
        $('#password').closest('.alr').find(".alr-t").text("")
        count++;
    }

    // Confirmation
    if(document.querySelector('#confirm')){
        if($('#confirm').val() == "" || $('#confirm').val() != $('#password').val()){
            if($('#confirm').val() == ""){
                if ($('#acceptTerms').prop('checked') || alert == true){
                    $('#confirm').closest('.alr').find(".alr-t").text("* The password confirmation cannot be empty")
                    $('#confirm').addClass("invalid")
                }
            }
    
            if($('#confirm').val() != $('#password').val()){
                if ($('#acceptTerms').prop('checked') || alert == true){
                    $('#confirm').closest('.alr').find(".alr-t").text("* The passwords don't match")
                    $('#confirm').addClass("invalid")
                }
            }
        }else{
            $('#confirm').removeClass("invalid")
            $('#confirm').closest('.alr').find(".alr-t").text("")
            count++;
        }
    }

    if(document.querySelector('#register_form')){
        if($('#acceptTerms').prop('checked')){
            count++;
        }

        if(count == 5){
            $('.set').attr("disabled", false)
            return true
        }else{
            $('.set').attr("disabled", true)
            $('.set .loader').addClass('hidden')
            $('.set p').removeClass('hidden')
            $('.hold').removeClass('show')
            return false
        }
    }

    if($('#login_form')){
        if(count == 2){
            $('.set').attr("disabled", false)
            return true
        }else{
            $('.set').attr("disabled", true)
            $('.set .loader').addClass('hidden')
            $('.set p').removeClass('hidden')
            $('.hold').removeClass('show')
            return false
        }
    }
}

$('#acceptTerms').click(()=>{
    if ($('#acceptTerms').prop('checked')){
        validator(true)
    }
})
$("input").on('input', ()=>{
    validator(false)
})

function signup(){
    if(validator(true)){
        if(document.querySelector('#register_form')){
            let email = String($('#email').val()).trim()
            let obj = {
                "__data__": {
                    "__user__":{
                        "company": $('#company').val(),
                        "email": email,
                        "country": $('#countries').val(),
                        "password": $('#password').val(),
                        "comfirm": $('#confirm').val(),
                        "policy": $('#acceptTerms').prop('checked'),
                    }
                }
            }
            
            $('.set .loader').removeClass('hidden')
            $('.set p').addClass('hidden')
            $('.hold').addClass('show')
            resetPasswordFields();

            $.ajax({
                url: './static/assets/country.json',
                type: 'GET',
                dataType: 'json'
            }).done(function(data) {
                data.forEach(function(country) {
                    const countryName = country.data.code.toLowerCase();
                    const isSelected = countryName === $('#countries').val();
                    if(isSelected){
                        obj['__data__']['__user__']['code_number'] = country.data.number;
                        obj['__data__']['__user__']['timezone'] = country.data.timezone;

                        $.ajax({
                            url: '/register',
                            type: 'POST',
                            data: JSON.stringify(obj),
                            contentType: 'application/json'
                        }).done(function(data) {
                            if(data?.status){
                                $('.set .loader').addClass('hidden')
                                $('.set p').removeClass('hidden')
                                $('.hold').removeClass('show')

                                $('.sign').addClass('hidden')
                                $('.email_comfirm').removeClass('hidden')

                                $('#text_').html(`Go to this post's inbox <b>${email}</b> if you don't have a message from us in your inbox, look in your spam folder. Although we don't usually get caught in spam filters.`)
                                
                                if(data?.link != null){
                                    $('.email_comfirm').append(`<a href="${data.link}" class="linkToEmail">Go to your mailbox</a>`)
                                }   
                            }else{
                                $('.set .loader').addClass('hidden')
                                $('.set p').removeClass('hidden')
                                $('.hold').removeClass('show')

                                if(data?.type == "email"){
                                    $('#email').closest('.alr').find(".alr-t").text(data['message'])
                                    $('#email').addClass("invalid")
                                }
                                
                                if(data?.type == "password"){
                                    $('#password').closest('.alr').find(".alr-t").text(data['message'])
                                    $('#password').addClass("invalid")
                                }
                                if(data?.type == "comfirm"){
                                    $('#password').closest('.alr').find(".alr-t").text(data['message'])
                                    $('#password').addClass("invalid")

                                    $('#confirm').closest('.alr').find(".alr-t").text(data['message'])
                                    $('#confirm').addClass("invalid")
                                }
                            }
                        })
                    }
                });
            });
        }

        if(document.querySelector('#login_form')){
            let obj = {
                "__data__": {
                    "__user__":{
                        "username": String($('#email').val()).trim(),
                        "password": $('#password').val(),
                    }
                }
            }
            $('.set .loader').removeClass('hidden')
            $('.set p').addClass('hidden')
            $('.hold').addClass('show')
            resetPasswordFields();

            $.ajax({
                url: '/login',
                type: 'POST',
                data: JSON.stringify(obj),
                contentType: 'application/json'
            }).done(function(data) {
                $('.set .loader').addClass('hidden')
                $('.set p').removeClass('hidden')
                $('.hold').removeClass('show')
                if(data?.status){
                    sessionStorage.setItem('token', data['token']);
                    if (sessionStorage.getItem('token')) {
                        window.location.href = "/set_token/" + sessionStorage.getItem('token');
                    }
                }else{
                    if(data?.type == "email"){
                        $('#email').closest('.alr').find(".alr-t").text(data['message'])
                        $('#email').addClass("invalid")
                    }
                    
                    if(data?.type == "password"){
                        $('#password').closest('.alr').find(".alr-t").text(data['message'])
                        $('#password').addClass("invalid")
                    }
                }
            })
        }
    }
}

$(window).on('keydown', (e)=>{
    if(e.keyCode == 13){
        signup();
    }
})

$('.set').click(()=>{
    signup()
})