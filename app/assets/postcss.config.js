module.exports = {
    ident: 'postcss-loader',
    syntax: 'postcss-scss',
    plugins: [
        require('postcss-easy-import'),
        require('postcss-advanced-variables'),
        require('postcss-atroot'),
        require('postcss-extend-rule'),
        require('postcss-preset-env'),
        require('postcss-property-lookup'),
        require('postcss-rem')({baseline: 18, fallback: true}),
        require('postcss-focus-visible'),
        require('postcss-map-get'),
        require('postcss-css-variables'),
        require('tailwindcss/nesting'),
        require('tailwindcss'),
        require('autoprefixer')({
            grid: 'autoplace'
        }),
        require('cssnano')({
            preset: 'default',
        })
    ]
}
