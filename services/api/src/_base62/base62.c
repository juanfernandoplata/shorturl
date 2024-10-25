#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <math.h>

const char BASE[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

static PyObject * encode( PyObject * self, PyObject * args ) {
    int n;

    if ( !PyArg_ParseTuple( args, "i", &n ) ) {
        return NULL;
    }

    char encoded[ 7 ] = "000000\0";

    int i = 5;
    while ( n > 0 ) {
        encoded[ i-- ] = BASE[ n % 62 ];
        n /= 62;
    }

    return Py_BuildValue( "s", encoded );
}

int char_to_base10( char c ) {
    if ( c > 90 ) {
        return 36 + ( c - 97 );
    }

    else if ( c > 57 ) {
        return 26 + ( c - 65 );
    }

    return c - 48;
}

static PyObject * decode( PyObject * self, PyObject * args ) {
    const char * encoded;

    if ( !PyArg_ParseTuple( args, "s", &encoded ) ) {
        return NULL;
    }

    int n = 0;

    for ( int i = 0; i < 6; i++ ) {
        n += char_to_base10( encoded[ i ] ) * pow( 62, 5 - i );
    }

    return Py_BuildValue( "i", n );
}

static PyMethodDef methods[] = {
    { "encode", encode, METH_VARARGS, "Encode an integer value to base62" },
    { "decode", decode, METH_VARARGS, "Decode an integer from base62" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "base62",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_base62( void ) {
    return PyModule_Create( &module );
}
