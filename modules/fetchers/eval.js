const process = require('process');

const stream = process.stdin;


f = function(p, a, c, k, e, d) {
    e = function(c) {
        return (c < a ? "" : e(parseInt(c / a))) + ((c = c % a) > 35 ? String.fromCharCode(c + 29) : c.toString(36))
    };
    if (!''.replace(/^/, String)) {
        while (c--) d[e(c)] = k[c] || e(c);
        k = [function(e) {
            return d[e]
        }];
        e = function() {
            return '\\w+'
        };
        c = 1;
    };
    while (c--)
        if (k[c]) p = p.replace(new RegExp('\\b' + e(c) + '\\b', 'g'), k[c]);
    return p;
}


stream.on("readable", function(){
	let data;
	while (data = this.read()){
		let test = data.toString().replace("\r\n").split("£");

		console.log(f(test[0], test[1], test[2], test[3].split('|'), 0, {}), "\r\nEOF");
	}
});
