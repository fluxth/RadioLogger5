export const setPageTitle = (title = null) => {
    const appName = 'Radio Logger 5 GUI'

    if (title === null)
        document.title = appName
    else
        document.title =  title + ' - ' + appName
}