script {
fun main() {
    let x: u64;
    if (true) () else x = 100;
    0x0::Transaction::assert(x == 100, 42);
}
}

// check: COPYLOC_UNAVAILABLE_ERROR
