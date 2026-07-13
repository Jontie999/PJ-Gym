const admin = require("firebase-admin");
const serviceAccount = require(process.env.GOOGLE_APPLICATION_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
const db = admin.firestore();

const USER_ID = "6LQ3KJW8rJfUlmwmEEvpWEJBXwk2";
const THRESHOLD = 0.5; // 50% deviation allowed

async function fixOutliers() {
  const workoutsRef = db.collection("users").doc(USER_ID).collection("workouts");
  const snapshot = await workoutsRef.orderBy("date").get();

  const workouts = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }));

  let lastValidVolumeByExercise = {};

  for (const w of workouts) {
    const exercise = w.exerciseName;
    const volume = w.totalVolume;

    if (!lastValidVolumeByExercise[exercise]) {
      lastValidVolumeByExercise[exercise] = volume;
      continue;
    }

    const lastValid = lastValidVolumeByExercise[exercise];

    const deviation = Math.abs(volume - lastValid) / lastValid;

    if (deviation > THRESHOLD) {
      console.log(
        `Outlier detected for ${exercise} on ${w.date}: ${volume} → fixing to ${lastValid}`
      );

      await workoutsRef.doc(w.id).update({
        totalVolume: lastValid
      });
    } else {
      lastValidVolumeByExercise[exercise] = volume;
    }
  }

  console.log("Outlier correction complete.");
}

fixOutliers().catch(console.error);
