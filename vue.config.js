const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  configureWebpack: {
    resolve: {
      fallback: {
        vm: require.resolve('vm-browserify'),
      },
    },
  },
})
