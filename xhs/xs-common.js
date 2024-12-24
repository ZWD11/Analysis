// 函数部分代码经过部分还原，所以和原官方不太一样

const { get_xs, cookie } = require('./xs.js')
cookiestr = cookie

function get_trace_id() {
    for (var t = "", e = 0; e < 16; e++)
        t += "abcdef0123456789".charAt(Math.floor(16 * Math.random()));
    return t
}
x_b3_traceid = get_trace_id()

headers = {
    "x-xray-traceid": "c9f9b2ccbaa332b61d4195fdfee73a1c"
}

function dictcookie(cookiestr) {
    return cookiestr.split(';')
        .reduce((acc,pair) => {
        const [key, value] = pair.trim().split('=');
        acc[key] = value;
        return acc
        },{});
}
cookieStr = dictcookie(cookiestr)

localStorage = { // 控制台自行打印补充完整 localStorage
    "MF_STATISTICS": "{\"timestamp\":1734920705197,\"visitTimes\":2,\"readFeedCount\":3}",
    "xhs_context_networkQuality": "UNKNOWN",
      getItem: function(arg) {
        return this[arg];
    }
}

sessionStorage = { // 控制台自行打印补充完整 sessionStorage
    "__SPA_REFER__": "https://www.xiaohongshu.com/search_result?keyword=%25E5%25B7%25B4%25E9%25BB%258E%25E4%25B8%2596%25E5%25AE%25B6track%25E9%259E%258B%25E5%25B8%25A6%25E7%25B3%25BB%25E6%25B3%2595&source=web_search_result_notes",
    "__SPA_LCP__/explore/675ab1510000000007009038": "reported",
    "__SPA_LCP__/search_result": "reported",
    "sc": "186",
    "__SPA_LCP__/explore/67668c87000000001301a6cc": "reported",
    "__SPA_LCP__/explore/676037210000000013009b38": "reported",
    "__SPA_LCP__/explore": "reported",
    setItem: function(key, value){
        this[key] = value
    },
    getItem: function(arg){
        return this[arg]
    }
}
  
encrypt_lookup =['Z', 'm', 's', 'e', 'r', 'b', 'B', 'o', 'H', 'Q', 't', 'N', 'P', '+', 'w', 'O', 'c', 'z', 'a', '/', 'L', 'p', 'n', 'g', 'G', '8', 'y', 'J', 'q', '4', '2', 'K', 'W', 'Y', 'j', '0', 'D', 'S', 'f', 'd', 'i', 'k', 'x', '3', 'V', 'T', '1', '6', 'I', 'l', 'U', 'A', 'F', 'M', '9', '7', 'h', 'E', 'C', 'v', 'u', 'R', 'X', '5']

var PULL_BLOCK_STATUS = 461, NONE_FINGERPRINT_STATUS = 462, RISK_LOGIN_STATUS = 465, RISK_SPAM_STATUS = 471, const_ORGANIZATION = "eR46sBuqF0fdw7KWFLYa", RC4_SECRET_VERSION = "1", LOCAL_ID_SECRET_VERSION = "0", RC4_SECRET_VERSION_KEY = "b1b1", LOCAL_ID_KEY = "a1", WEB_ID_KEY = "webId", GID = "gid", MINI_BROSWER_INFO_KEY = "b1", PROFILE_COUNT_KEY = "p1", PROFILE_TRIGGER_TIME_KEY = "ptt", PROFILE_SERVER_TIME_KEY = "pst", SIGN_COUNT_KEY = "sc", XHS_SIGN = "websectiga", XHS_POISON_ID = "sec_poison_id", APP_ID_NAME = "xsecappid", PLATFORM_CODE_MAP

function a0_0x5b7a() {
    var e = ["XqrEV", "tsFKp", "oDsdr", "kNFav", "nvwrG", "xdSEr", "WVHkM", "pKrzH", "ize", "zXJTf", "xOUsZ", "ule", "5278889biZuxO", "CnHpM", "QvpcT", "hasOwnP", "zgSxz", "PGjnV", "eAt", "cOFWl", "bxwCP", "Bvk6/7=", "EVbLj", "ZdEqk", "qeWwX", "3|4|0", "hCNPL", "asBytes", "GSFdP", "456789+", "LoRvO", "615820BhUAOn", "ymCct", "endian", "POkwq", "SRrZy", "x3VT16I", "UPJZx", "userAge", "YrxgM", "KtsHt", "oRVoy", "VsIqu", "IpOsG", "edJIP", "BRJOV", " Object", "call", "uOSvV", "bZkXX", "yoGhc", "Bytes", "OajSo", "hcAOZ", "TCndc", "5cZzete", "ESuxn", "PrtZi", "xVBWW", "default", "sHwlc", "GOcHL", "ZmserbB", "IQGuL", "qHhny", "stringT", "navigat", "mKGlM", "FyIgG", "random", "QLlYm", "|2|5|3|", "roperty", "Hex", "nt ", "bMCpP", "functio", "asStrin", "EuFYO", "cVte9UJ", "xDUPY", "UXDJt", "KjSDH", "FUNYr", "yXJkX", "pngG8yJ", "zRDHC", "cIDrv", "split", "FnlQW", "riAqL", "GmOGO", "vzZEC", "slice", "nLgjc", "stringi", "WyPxe", "BrDUy", "qpboh", "CZXSy", "nMHVI", "BiXDC", "UJXcT", "Words", "DLkoH", "_isBuff", "ABCDEFG", "OsFze", "oHQtNP+", "szLAG", "dLJAT", "fnzLJ", "yxUKW", "NBKNO", "ntybJ", " Array]", "WqCRu", "oOWUm", "Ehneo", "wxDaz", "OPQRSTU", "fpiZZ", "_ff", "dKIRL", "cBQxr", "EEXKq", "string", "_gg", "eOqDH", "WGwra", "0DSfdik", "a2r1ZQo", "charCod", "fcJZj", "bytesTo", "_hh", "amMEV", "test", "qrstuvw", "|7|1|8|", "LpfE8xz", "2484436oCuHeM", "substr", "wQIlT", "ptuhI", "iHgZg", "eoHfh", "|0|5|4|", "rable", "String", "eMgNI", "alert", " argume", "HcQtD", "6|9|2|5", "yHssg", "lQrIV", "wrNWJ", "LDZzf", "zUdri", "lOvpG", "PKfMB", "uvAcE", "FpaZM", "A4NjFqY", "xTjMm", "bjRCG", "prototy", "zVuPl", "hECvuRX", "WnPGl", "xSAOj", "rotl", "svcRz", "3|1|0|5", "binary", "MzIIu", "weYxc", "adztu", "constru", "hyoem", "WZJNP", "yRDQP", "rcibI", "noYSu", "vtlxb", "otnJK", "kNwEp", "swDsC", "wglkV", "isArray", "undefin", "KdZPH", "readFlo", "dQbKw", "indexOf", "4|0|1|7", "_digest", "length", "VoKJS", "XPKrF", "jklmnop", "DNiKZ", "426432ompcln", "nacEY", "wMPvT", "ARyzf", "XYjop", "ycqKc", "wordsTo", "push", "oILkc", "MKhPs", "KBzpN", "charAt", "ekWdI", "XPqkg", "ble", "__esMod", "SritR", "sQYkV", "REfgq", "vVhJX", "18BZGxCc", "oBytes", "cdefghi", "JQMmQ", "LbTtx", "3|1|2|7", "CjuVd", "vpDix", "EJkCm", "JtNQV", "rKkrc", "koOgW", "NqSaj", "rCode", "|2|4", "u5wPHsO", "lUAFM97", "join", "bin", "QnDGB", "WJQkw", "kAfVR", "KJEUB", "ZgtEH", "xvYNk", "JSPgp", "YUclm", "lOQoH", "UeOpE", "toStrin", "floor", "bcExD", "1138338tisTPs", "oJhNC", "0XTdDgM", "defineP", "iamspam", "XgEHW", "VMlXa", "NuESW", "exports", "KblCWi+", "KWIPM", "configu", "LKjbB", "[object", "zujnu", "UxShG", "enumera", "zvigo", "isBuffe", "OIUKI", "vrtAe", "yRnhISG", "nNswt", "CETMA", "yeewt", "FjySX", "Wrzlo", "_blocks", "TnNqZ", "hJWBc", "GXwNT", "rFfom", "wlMIe", "q42KWYj", "XvbAQ", "VJcfp", "ctor", "utf8", "get", "Bkmpz", "ZMLCD", "OAxXI", "HIJKLMN", "RxubR", "DwSEn", "RgFVi", "cGydf", "iMrwJ", "WSLjK", "UgrKe", "replace", "511077NzzaGU", "hcUaR", "IhPtE", "xGGTF", "gmCro", "MTpPz", "MhAtY", "KJfAb", "VWXYZab", "dBEUD", "YKVcV", "pow", "PFcHx", "CRGHn", "GYFzd", "usNzj", "_ii", "RdKXK", "pYmNK", "uGyia", "cmTtP", "wOcza/L", "IXiGa", "xyz0123", "BaAov", "lYBrT", "DRmvP", "XmPnm", "aWCCy", "uGGKn", "encodin", "xYaZZ", "atLE", "gaXnw", "hpvhj", "size", "QaVmD", "getTime", "xwjZM", "Illegal", "1915088LOuxXC", "lRsmX", "fromCha"];
    return (a0_0x5b7a = function() {
        return e
    }
    )()
}

function a0_0x2e01(e, t) {
    var r = a0_0x5b7a();
    return (a0_0x2e01 = function(e, t) {
        return r[e -= 125]
    }
    )(e, t)
}

function a0_0xb6ac53(e, t) {
    return a0_0x2e01(e - -723, t)
}

function encrypt_tripletToBase64(e) {
    return encrypt_lookup[(e >> 18) & 63] + 
           encrypt_lookup[(e >> 12) & 63] + 
           encrypt_lookup[(e >> 6) & 63] + 
           encrypt_lookup[63 & e];
}

function encrypt_encodeChunk(e, t, r) {
    const w = [];
    for (let _ = t; _ < r; _ += 3) {
        const n = ((e[_] << 16) & 16711680) + 
                 ((e[_ + 1] << 8) & 65280) + 
                 (e[_ + 2] & 255);
        w.push(encrypt_tripletToBase64(n));
    }
    return w.join("");
}

function encrypt_b64Encode(e) {
    const X = e.length;
    const K = X % 3;
    const $ = [];
    const z = 16383;

    for (let Y = 0, Q = X - K; Y < Q; Y += z) {
        $.push(encrypt_encodeChunk(e, Y, Y + z > Q ? Q : Y + z));
    }

    if (K === 1) {
        const J = e[X - 1];
        $.push(encrypt_lookup[J >> 2] + 
               encrypt_lookup[(J << 4) & 63] + 
               "==");
    } else if (K === 2) {
        const J = (e[X - 2] << 8) + e[X - 1];
        $.push(encrypt_lookup[J >> 10] + 
               encrypt_lookup[(J >> 4) & 63] + 
               encrypt_lookup[(J << 2) & 63] + 
               "=");
    }

    return $.join("");
}

function encrypt_encodeUtf8(e) {
    function T(e, t) {
        return a0_0xb6ac53(t - 194, e);
    }
    
    var E = {
        IQGuL: function(e, t) {
            return e(t);
        },
        kNFav: function(e, t) {
            return e < t;
        },
        wlMIe: function(e, t) {
            return e === t;
        },
        RxubR: function(e, t) {
            return e + t;
        },
        edJIP: function(e, t) {
            return e + t;
        },
        QaVmD: function(e, t) {
            return e + t;
        },
        KtsHt: function(e, t, r) {
            return e(t, r);
        }
    };

    var k = E.IQGuL(encodeURIComponent, e);
    var S = [];

    for (var x = 0; x < k.length; x++) {
        var A = k.charAt(x);
        if (A === "%") {
            var R = k.charAt(x + 1) + k.charAt(x + 2);
            var C = parseInt(R, 16);
            S.push(C);
            x += 2;
        } else {
            S.push(A.charCodeAt(0));
        }
    }
    
    return S;
}

var encrypt_mcr = function(e) {
    var t = 7
      , r = 36
      , n = 185
      , o = 160
      , i = 91
      , a = 165
      , s = 112
      , u = 46
      , c = 86
      , l = 48
      , f = 265
      , p = 760
      , d = 596
      , v = 740
      , h = 613
      , g = 507
      , m = 471
      , y = 414
      , w = 588
      , _ = 544
      , b = 654
      , E = 589
      , k = 500
      , T = 658
      , S = 485
      , x = 479
      , A = 486
      , R = 418
      , C = 586
      , I = 665
      , O = 437
      , P = 531
      , N = 531
      , L = 439
      , M = {};
    M[q(-33, 19)] = function(e, t) {
        return e === t
    }
    ,
    M[q(t, r)] = q(19, n),
    M[q(-146, -70)] = function(e, t) {
        return e < t
    }
    ,
    M[q(o, 11)] = function(e, t) {
        return e ^ t
    }
    ,
    M[q(-176, -i)] = function(e, t) {
        return e ^ t
    }
    ,
    M[q(123, 9)] = function(e, t) {
        return e & t
    }
    ,
    M[q(a, s)] = function(e, t) {
        return e >>> t
    }
    ,
    M[q(-189, -u)] = function(e, t) {
        return e ^ t
    }
    ;
    for (var B, D, F = M, j = 3988292384, U = 256, H = []; U--; H[U] = F[q(c, s)](B, 0))
        for (D = 8,
        B = U; D--; )
            B = 1 & B ? F[q(-l, -u)](F[q(f, 112)](B, 1), j) : F[q(87, s)](B, 1);
    function q(e, t) {
        return a0_0xb6ac53(t - L, e)
    }
    return function(e) {
        function t(e, t) {
            return q(e, t - 577)
        }
        if (F[t(p, d)]('string','string')) {
            for (var r = 0, n = -1; F[t(446, g)](r, e[t(m, 485)]); ++r)
                n = H[F[t(y, w)](255 & n, e[t(_, 419) + t(696, b)](r))] ^ n >>> 8;
            return F[t(E, 486)](n, -1) ^ j
        }
        for (r = 0,
        n = -1; F[t(k, g)](r, e[t(T, S)]); ++r)
            n = F[t(x, A)](H[F[t(R, C)](n, 255) ^ e[r]], F[t(I, 689)](n, 8));
        return F[t(O, P)](F[t(502, N)](n, -1), j)
    }
}();

function getSigCount(e) {
    var t = Number(sessionStorage.getItem(SIGN_COUNT_KEY)) || 0;
    return e && (t++,
    sessionStorage.setItem(SIGN_COUNT_KEY, t.toString())),
    t
}

function get_xs_t_common(search_id, keyword) {
    var id = search_id, key = keyword
    var x_s_t = get_xs(id, key)
    var c = x_s_t['X-t'] || ""
    , l = x_s_t['X-s'] || ""
    , f = headers["X-Sign"] || ""
    , p = getSigCount(c && l || f)
    , d = localStorage.getItem(MINI_BROSWER_INFO_KEY)
    , v = localStorage.getItem(RC4_SECRET_VERSION_KEY) || RC4_SECRET_VERSION
    , h = {
    s0: 5,
    s1: "",
    x0: v,
    x1: "3.8.7",
    x2: "Windows",
    x3: "xhs-pc-web",
    x4: "4.48.0",
    x5: cookieStr["a1"],
    x6: c,
    x7: l,
    x8: d,
    x9: encrypt_mcr("".concat(c) + l + d),
    x10: p
    }
    x_common = encrypt_b64Encode(encrypt_encodeUtf8(JSON.stringify(h)))
    return {
        x_common: x_common,
        x_s_t: x_s_t
    }
}