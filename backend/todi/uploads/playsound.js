function play_sound(path) {
  const audio = new Audio(`${path}.mp3`)
  audio.play()
}
