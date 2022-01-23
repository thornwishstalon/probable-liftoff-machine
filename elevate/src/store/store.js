import { createStore } from 'vuex'


// Create a new store instance.
export const store = createStore({
    state : {
        currentLevel: -1,
        nextTrips: [1],
        moving: false
    },
    getters:{
        currentLevel (state){
            return state.currentLevel
        },
        nextTrips (state){
            return state.nextTrips
        },
        isMoving (state){
            return state.moving
        },
        isActive: (state) => (floor) => {
            return state.nextTrips.includes(floor)
        }
    },
    mutations: {
        updateState (state, newState){
            state.moving = newState.moving
            state.nextTrips = newState.nextTrips
            state.currentLevel = newState.currentLevel
        }
    }
})

