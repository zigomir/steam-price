if (phantom.args.length < 3) {
    // console.log('Usage: phantomjs steamAppID lowerThanPrice email');
    phantom.exit();
} else {
    var url = 'http://store.steampowered.com/app/' + phantom.args[0];
    var lowerThanPrice = phantom.args[1];
    var email = phantom.args[2];

    // meat of the program, but also slow
    loadSteamSite(url, lowerThanPrice, email);
}

function parsePrice(priceStr) {
    var priceLength = priceStr.indexOf(',') + 3;
    var result = priceStr.substring(0, priceLength).replace(',', '.');
    return parseFloat(result);
}

function loadSteamSite(url, lowerThanPrice, email) {
    if (phantom.state.length === 0) {
        // console.log('Opening ' + url);
        phantom.state = 'steam_app';
        phantom.open(url);
    } else {
        var priceStr = '0,00€';
        // discount price class = discount_final_price
        try {
            priceStr = document.querySelectorAll('div.discount_final_price')[0].innerHTML;
        } catch (err) {
            // console.log('This game isnt discounted!');
            // regular price class = game_purchase_price price
            try {
                priceStr = document.querySelectorAll('div.game_purchase_price')[0].innerHTML;
            } catch (err) {
                // console.log('This game isnt discounted nor has purchase price
                // :|');
            }
        }

        // console.log('Price string: ' + priceStr);

        var priceNumber = parsePrice(priceStr);
        // console.log('Price number: ' + priceNumber);

        if (priceNumber <= lowerThanPrice) {
            console.log(email);
            console.log('Fckye, price for the game on url id '
                    + phantom.args[0] + ' (' + url + ')'
                    + ' is lower or same than ' + lowerThanPrice + ' EUR.');
            // console.log('I must send this info to your email (' + email +
            // ')');
        } else {
            // console.log('Sorry, price still more than ' + lowerThanPrice + '
            // EUR.');
        }

        phantom.exit();
    }
}
