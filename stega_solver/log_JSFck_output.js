var fs = require('fs')

const filename = process.argv.slice(2)[0]

var jsfuckCode = ""
try {
  jsfuckCode = fs.readFileSync(filename, 'utf8')
} catch (err) {
  console.error(err)
}

jsfCodeOutput = eval(jsfuckCode)
console.log(jsfCodeOutput)