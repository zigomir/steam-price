var priceStr = '4,99€'
var priceNumber = parsePrice(priceStr);
console.log(priceStr);
console.log(priceNumber);

phantom.exit();

function parsePrice(priceStr) {
	var priceLength = priceStr.indexOf(',') + 3;
	var result = priceStr.substring(0, priceLength).replace(',', '.');
	return parseFloat(result);
}