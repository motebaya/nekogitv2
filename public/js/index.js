/**
 * jquery index page
 * @github.com/motebaya - 15.01.2023
 *
 */

const setTheme = (theme) => {
  $("html").attr("data-bs-theme", theme);
  localStorage.setItem("theme", theme);
  $(".poi-svg").attr(
    "src",
    theme === "dark" ? "/img/poi-light.svg" : "/img/poi.svg"
  );
};

$(window).on("load", () => {
  let localtheme = localStorage.getItem("theme");
  if (localtheme) {
    setTheme(localtheme);
  }
});

$(function () {
  $(window).on("scroll", function () {
    if ($(this).scrollTop() > 300) {
      $(".back-to-top").fadeIn();
    } else {
      $(".back-to-top").fadeOut();
    }
  });
  $(".dropdown-item").on("click", function (e) {
    e.preventDefault();
    let theme = $(this).data("theme");
    setTheme(
      theme === "auto"
        ? window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light"
        : theme
    );
  });
});
