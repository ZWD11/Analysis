window = global;
var key;
var dash;
rr = {
    dashParam: function() {
        return {
            qd_v: "a1",
            tm: (new Date).getTime()
        }
    },
    dashParam_server: function() {
        return {
            qd_v: "2in",
            tm: (new Date).getTime()
        }
    },
    dash: function(e) {
        let t, i, r, n, s = e;
        for (t = 0; t < 4; t++)
            for (i = 0; i < 2; i++)
                for (r = 0; r < 4; r++)
                    n = (70 * t + 677 * i + 21 * r + 87 * t * i * r + 59) % 30,
                    n += n < 9 ? 48 : 88,
                    s += String.fromCharCode(n);
        return s
    },
    qd_sc: function(e) {
        let t, i, r, n, s = e;
        for (t = 0; t < 2; t++)
            for (i = 0; i < 4; i++)
                for (r = 0; r < 4; r++)
                    n = (85 * t + 76 * i + 33 * r + 17 * t * i * r + 9) % 31,
                    n += n < 10 ? 48 : 88,
                    s += String.fromCharCode(n);
        return s
    },
    qd_v: 71,
    ibt: function(e) {
        let t, i, r, n, s = e;
        for (t = 0; t < 2; t++)
            for (i = 0; i < 4; i++)
                for (r = 0; r < 4; r++)
                    n = (103 * t + 21 * i + 7 * r + 14 * t * i * r + 7) % 32,
                    n += n < 10 ? 48 : 87,
                    s += String.fromCharCode(n);
        return s
    },
    ib: 81
}
var d = function(e, t) {
    return e << t | e >>> 32 - t
}
  , l = function(e, t) {
    var i, r, n, s, a;
    return n = 2147483648 & e,
    s = 2147483648 & t,
    a = (1073741823 & e) + (1073741823 & t),
    (i = 1073741824 & e) & (r = 1073741824 & t) ? 2147483648 ^ a ^ n ^ s : i | r ? 1073741824 & a ? 3221225472 ^ a ^ n ^ s : 1073741824 ^ a ^ n ^ s : a ^ n ^ s
}
  , u = function(e, t, i, r, n, s, a) {
    return e = l(e, l(l(function(e, t, i) {
        return e & t | ~e & i
    }(t, i, r), n), a)),
    l(d(e, s), t)
}
  , c = function(e, t, i, r, n, s, a) {
    return e = l(e, l(l(function(e, t, i) {
        return e & i | t & ~i
    }(t, i, r), n), a)),
    l(d(e, s), t)
}
  , h = function(e, t, i, r, n, s, a) {
    return e = l(e, l(l(function(e, t, i) {
        return e ^ t ^ i
    }(t, i, r), n), a)),
    l(d(e, s), t)
}
  , p = function(e, t, i, r, n, s, a) {
    return e = l(e, l(l(function(e, t, i) {
        return t ^ (e | ~i)
    }(t, i, r), n), a)),
    l(d(e, s), t)
}
  , f = function(e) {
    for (var t, i = e.length, r = i + 8, n = 16 * ((r - r % 64) / 64 + 1), s = Array(n - 1), a = 0, o = 0; o < i; )
        a = o % 4 * 8,
        s[t = (o - o % 4) / 4] = s[t] | e.charCodeAt(o) << a,
        o++;
    return a = o % 4 * 8,
    s[t = (o - o % 4) / 4] = s[t] | 128 << a,
    s[n - 2] = i << 3,
    s[n - 1] = i >>> 29,
    s
}
  , m = function(e) {
    var t, i = "", r = "";
    for (t = 0; t <= 3; t++)
        i += (r = "0" + (e >>> 8 * t & 255).toString(16)).substr(r.length - 2, 2);
    return i
}
  , g = function(e) {
    e = e.replace(/\x0d\x0a/g, "\n");
    for (var t = "", i = 0; i < e.length; i++) {
        var r = e.charCodeAt(i);
        r < 128 ? t += String.fromCharCode(r) : r > 127 && r < 2048 ? (t += String.fromCharCode(r >> 6 | 192),
        t += String.fromCharCode(63 & r | 128)) : (t += String.fromCharCode(r >> 12 | 224),
        t += String.fromCharCode(r >> 6 & 63 | 128),
        t += String.fromCharCode(63 & r | 128))
    }
    return t
};
function v(e) {
    e += "";
    var t, i, r, n, s, a, o, d, v, _ = Array();
    for (e = g(e),
    _ = f(e),
    a = 1732584193,
    o = 4023233417,
    d = 2562383102,
    v = 271733878,
    t = 0; t < _.length; t += 16)
        i = a,
        r = o,
        n = d,
        s = v,
        a = u(a, o, d, v, _[t + 0], 7, 3614090360),
        v = u(v, a, o, d, _[t + 1], 12, 3905402710),
        d = u(d, v, a, o, _[t + 2], 17, 606105819),
        o = u(o, d, v, a, _[t + 3], 22, 3250441966),
        a = u(a, o, d, v, _[t + 4], 7, 4118548399),
        v = u(v, a, o, d, _[t + 5], 12, 1200080426),
        d = u(d, v, a, o, _[t + 6], 17, 2821735955),
        o = u(o, d, v, a, _[t + 7], 22, 4249261313),
        a = u(a, o, d, v, _[t + 8], 7, 1770035416),
        v = u(v, a, o, d, _[t + 9], 12, 2336552879),
        d = u(d, v, a, o, _[t + 10], 17, 4294925233),
        o = u(o, d, v, a, _[t + 11], 22, 2304563134),
        a = u(a, o, d, v, _[t + 12], 7, 1804603682),
        v = u(v, a, o, d, _[t + 13], 12, 4254626195),
        d = u(d, v, a, o, _[t + 14], 17, 2792965006),
        o = u(o, d, v, a, _[t + 15], 22, 1236535329),
        a = c(a, o, d, v, _[t + 1], 5, 4129170786),
        v = c(v, a, o, d, _[t + 6], 9, 3225465664),
        d = c(d, v, a, o, _[t + 11], 14, 643717713),
        o = c(o, d, v, a, _[t + 0], 20, 3921069994),
        a = c(a, o, d, v, _[t + 5], 5, 3593408605),
        v = c(v, a, o, d, _[t + 10], 9, 38016083),
        d = c(d, v, a, o, _[t + 15], 14, 3634488961),
        o = c(o, d, v, a, _[t + 4], 20, 3889429448),
        a = c(a, o, d, v, _[t + 9], 5, 568446438),
        v = c(v, a, o, d, _[t + 14], 9, 3275163606),
        d = c(d, v, a, o, _[t + 3], 14, 4107603335),
        o = c(o, d, v, a, _[t + 8], 20, 1163531501),
        a = c(a, o, d, v, _[t + 13], 5, 2850285829),
        v = c(v, a, o, d, _[t + 2], 9, 4243563512),
        d = c(d, v, a, o, _[t + 7], 14, 1735328473),
        o = c(o, d, v, a, _[t + 12], 20, 2368359562),
        a = h(a, o, d, v, _[t + 5], 4, 4294588738),
        v = h(v, a, o, d, _[t + 8], 11, 2272392833),
        d = h(d, v, a, o, _[t + 11], 16, 1839030562),
        o = h(o, d, v, a, _[t + 14], 23, 4259657740),
        a = h(a, o, d, v, _[t + 1], 4, 2763975236),
        v = h(v, a, o, d, _[t + 4], 11, 1272893353),
        d = h(d, v, a, o, _[t + 7], 16, 4139469664),
        o = h(o, d, v, a, _[t + 10], 23, 3200236656),
        a = h(a, o, d, v, _[t + 13], 4, 681279174),
        v = h(v, a, o, d, _[t + 0], 11, 3936430074),
        d = h(d, v, a, o, _[t + 3], 16, 3572445317),
        o = h(o, d, v, a, _[t + 6], 23, 76029189),
        a = h(a, o, d, v, _[t + 9], 4, 3654602809),
        v = h(v, a, o, d, _[t + 12], 11, 3873151461),
        d = h(d, v, a, o, _[t + 15], 16, 530742520),
        o = h(o, d, v, a, _[t + 2], 23, 3299628645),
        a = p(a, o, d, v, _[t + 0], 6, 4096336452),
        v = p(v, a, o, d, _[t + 7], 10, 1126891415),
        d = p(d, v, a, o, _[t + 14], 15, 2878612391),
        o = p(o, d, v, a, _[t + 5], 21, 4237533241),
        a = p(a, o, d, v, _[t + 12], 6, 1700485571),
        v = p(v, a, o, d, _[t + 3], 10, 2399980690),
        d = p(d, v, a, o, _[t + 10], 15, 4293915773),
        o = p(o, d, v, a, _[t + 1], 21, 2240044497),
        a = p(a, o, d, v, _[t + 8], 6, 1873313359),
        v = p(v, a, o, d, _[t + 15], 10, 4264355552),
        d = p(d, v, a, o, _[t + 6], 15, 2734768916),
        o = p(o, d, v, a, _[t + 13], 21, 1309151649),
        a = p(a, o, d, v, _[t + 4], 6, 4149444226),
        v = p(v, a, o, d, _[t + 11], 10, 3174756917),
        d = p(d, v, a, o, _[t + 2], 15, 718787259),
        o = p(o, d, v, a, _[t + 9], 21, 3951481745),
        a = l(a, i),
        o = l(o, r),
        d = l(d, n),
        v = l(v, s);
    return (m(a) + m(o) + m(d) + m(v)).toLowerCase()
}
key = v;
dash = rr.dash
// r = '/dash?tvid=2337210470337500&bid=300&vid=2e75666d86d1663fe3194657c05a9ad6&src=01010031010000000000&vt=0&rs=1&uid=&ori=pcw&ps=1&k_uid=b0f3d36f9ca820ea7d76810d654d57ab&pt=0&d=0&s=&lid=0&cf=0&ct=0&authKey=223db45f976d4ce72f8595e1aff9fc53&k_tag=1&dfp=a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f&locale=zh_cn&pck=&up=&sr=1&cpt=0&qd_v=a1&tm=1733370653180&k_ft1=706436220846084&k_ft4=1161221786574852&k_ft5=137573171201&k_ft7=4&fr_1020=120_120_120_120_120_120&fr_800=120_120_120_120_120_120&fr_600=120_120_120_120_120_120&fr_500=120_120_120_120_120_120&fr_300=120_120_120_120_120_120&bop=%7B%22version%22%3A%2210.0%22%2C%22dfp%22%3A%22a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f%22%2C%22b_ft1%22%3A24%7D&ut=0'
// var rf = v(dash(r));

// text = 'd41d8cd98f00b204e9800998ecf8427e' + 1733370653180 + "" + 2337210470337500
// var authKey = v(text);

// // a = '2337210470337500'
// // console.log(key(a));
// console.log(rf);
// console.log(authKey);

