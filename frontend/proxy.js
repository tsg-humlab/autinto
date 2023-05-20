const express = require('express')
const { createProxyMiddleware } = require('http-proxy-middleware')

const app = express()
const port = 3000

app.use('/additional-files/main.js', createProxyMiddleware({
  target: 'http://localhost:3001/static/js/bundle.js',
  ignorePath: true,
}))

app.use(express.static('book/build'))

app.listen(port, () => console.log(`Proxy running on port ${port}`))
