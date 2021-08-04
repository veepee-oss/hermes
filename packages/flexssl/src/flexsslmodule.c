#include <Python.h>
#include <openssl/ssl.h>

/* ---------------------------------------------
   ---- Wrap C objects in Python Objects
   ---------------------------------------------*/

typedef struct {
    PyObject_HEAD
    SSL_CTX *ctx;
} PySSLContextWrapper;



/* ---------------------------------------------
   ---- Module Methods definitions
   ---------------------------------------------*/

static PyObject *method_set_sigalgs(PyObject *self, PyObject *args) {
    char *sigalgslist = NULL;
    PySSLContextWrapper *Pyctx = NULL;
    
    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "sO", &sigalgslist, &Pyctx)) {
        return NULL;
    }
    
    /* Set the signatures */
    int ret = SSL_CTX_set1_sigalgs_list(Pyctx->ctx, sigalgslist);
    if (ret == 0) {
        PyErr_SetString(PyExc_ValueError, "Cannot set the signatures ! Please check if these are correct !");
        return NULL;
    }

    Py_RETURN_NONE;
}

/* ---------------------------------------------
   ---- Boilerplate code for CFFI
   ---------------------------------------------*/

static PyMethodDef flexsslMethods[] = {
    {"set_sigalgs", method_set_sigalgs, METH_VARARGS, "Python interface for SSL_CTX_set1_sigalgs_list C OpenSSL library function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef flexsslModule = {
    PyModuleDef_HEAD_INIT,
    "flexssl",
    "Advanced and more Flexible Python interface for the OpenSSL C library",
    -1,
    flexsslMethods
};

PyMODINIT_FUNC PyInit_flexssl(void) {
    return PyModule_Create(&flexsslModule);
}