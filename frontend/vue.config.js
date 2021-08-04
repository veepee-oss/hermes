module.exports = {
    runtimeCompiler: true,
    productionSourceMap: false,

    devServer: {
        host: '0.0.0.0',
        disableHostCheck: true,
        port: 80,
        progress: false
    },

    publicPath: process.env.NODE_ENV === 'production'
        ? './'
        : '/'
}
