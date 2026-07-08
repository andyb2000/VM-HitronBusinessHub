function randomize(words, paranoia) {
    return sjcl.random.randomWords(words, paranoia);
}

/* Encrypt a message */
function doEncrypt(key, text) {
    if (!key || !text) {
        return;
    }

    var p = { adata: randomize(1, 0),
                iv: randomize(4, 0),
                salt: randomize(2, 0),
                iter: 10000,
                mode: 'gcm',
                ts: 64,
                ks: 128 };

    var ciphertext = sjcl.encrypt(key, text, p);
    /* console.log("ciphertext: " + ciphertext); */

    return ciphertext;
}

/* Decrypt a message */
function doDecrypt(password, ciphertext) {
    if (!password || !ciphertext) {
        return;
    }

    if (ciphertext.match("{")) {
        try {
            var plaintext = sjcl.decrypt(password, ciphertext);
        } catch(e) {
            return;
        }
        return plaintext;
    }
}