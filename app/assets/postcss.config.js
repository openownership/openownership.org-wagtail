module.exports = {
    ident: 'postcss-loader',
    syntax: 'postcss-scss',
    plugins: [
        require('postcss-easy-import'),
        require('precss'),
        require('postcss-rem')({baseline: 18, fallback: true}),
        require('postcss-focus-visible'),
        require('postcss-map-get'),
        require('postcss-css-variables'),
        require('tailwindcss'),
        require('autoprefixer')({
            grid: 'autoplace'
        }),
        require('cssnano')({
            preset: 'default',
        })
    ]
}
