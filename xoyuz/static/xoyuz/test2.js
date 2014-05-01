factorial = function(x) {
    if (x === 0) {
        return 1;
    } else {
        return factorial(x - 1) * x;
    }
}
