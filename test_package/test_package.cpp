#include <cstdlib>
#include <iostream>
#include "sodium.h"

int main()
{
    if (sodium_init() < 0)
        return EXIT_FAILURE;
    return EXIT_SUCCESS;
}
