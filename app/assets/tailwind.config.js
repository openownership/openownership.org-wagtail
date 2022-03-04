module.exports = {
    content: ['./../templates/**/*.jinja'],
    theme: {
      extend: {},
      colors: {
        white: '#FFFFFF',
        transparent: 'transparent',
        black: '#000000',
        text: {
            main: '#242424',
            secondary: '#626A6E'
        },
        links: {
            link: '#108484',
            hover: '#3027A8',
            visited: '#634F8F',
            active: '#242424'
        },
        border: {
            main: '#B1B4B6',
            input: '#242424',
            newsletter: '#626A6E',
            table: '#D3DBDB',
            data: '#979797'
        },
        focus: {
            main: '#DCEEFF'
        },
        error: {
            main: '#CA4D2B'
        },
        blue: {
          light: '#DCEEFF',
          cloud: '#4A576B',
          medium: '#3C31D5',
          dark: '#363F4E'
        },
        grey: {
          light: '#F7F7F7',
          medium: '#B1B4B6',
          dark: '#505050',
          darker: '#2F4549'
        }

      },
      borderWidth: {
        DEFAULT: '1px',
        '0': '0',
        '2': '2px',
        '3': '3px',
        '4': '4px',
        '6': '6px',
        '8': '8px',
      },
      fontFamily: {
        display: [
          'PlayfairDisplay',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          '"Noto Sans"',
          'sans-serif',
          '"Apple Color Emoji"',
          '"Segoe UI Emoji"',
          '"Segoe UI Symbol"',
          '"Noto Color Emoji"',
        ],
        body: [
          'Arimo',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          '"Noto Sans"',
          'sans-serif',
          '"Apple Color Emoji"',
          '"Segoe UI Emoji"',
          '"Segoe UI Symbol"',
          '"Noto Color Emoji"',
        ],
      },
      fontSize: {
        14: ['0.875rem', '1.625rem'],
        16: ['1rem', '1.625rem'],
        18: ['1.125rem', '1.5rem'],
        19: ['1.188rem', '1.75rem'],
        20: ['1.25rem', '1.625rem'],
        21: ['1.313rem', '1.813rem'],
        25: ['1.563rem', '1.875rem'],
        26: ['1.625rem', '2.5rem'],
        35: ['2.188rem', '2.813rem'],
        36: ['2.25rem', '3.75rem'],
        45: ['2.813rem', '3.125rem'],
        50: ['3.125rem', '3.563rem']
      }
    },
    plugins: [],
  }
  