// Seeded random number generator for daily randomization
class SeededRandom {
    constructor(seed) {
        this.seed = seed % 2147483647;
        if (this.seed <= 0) this.seed += 2147483646;
    }
    
    next() {
        this.seed = (this.seed * 16807) % 2147483647;
        return (this.seed - 1) / 2147483646;
    }
}

// Shuffle function using seeded random
function shuffle(array) {
    const today = new Date();
    const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
    
    const rng = new SeededRandom(seed);
    const result = [...array]; // Create a copy to avoid mutating the original
    
    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(rng.next() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }
    
    return result;
}

document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Simulate long loading
        // await new Promise(resolve => setTimeout(resolve, 2000));
        const spinner = document.getElementById('spinner');

        // Fetch the data from the backend
        const response = await fetch('./backend/database.json');
        const people = await response.json();
        
        // Get the template card and the people container
        const templateCard = document.getElementById('person');
        templateCard.removeAttribute('hidden');
        const peopleContainer = document.getElementById('people').parentElement; // This gets the row container
        
        // Loop through each person in the original order to add them
        people.forEach((person, index) => {
            // Clone the template card
            const cardClone = templateCard.parentElement.cloneNode(true); // Clone the col-lg-4 wrapper
            const personCard = cardClone.querySelector('#person');
            
            // Update the card ID to be unique
            personCard.id = `person-${person.id}`;
            
            // Update the person information
            personCard.querySelector('#firstName').textContent = person.first_name;
            personCard.querySelector('#lastName').textContent = person.last_name;
            personCard.querySelector('#position').textContent = person.position;
            personCard.querySelector('#description').textContent = person.description;
            
            // Handle social links
            const linksContainer = personCard.querySelector('#links');
            linksContainer.innerHTML = ''; // Clear existing links
            
            // Add custom links
            if (person.links && person.links.length > 0) {
                person.links.forEach(link => {
                    const linkElement = document.createElement('a');
                    linkElement.href = link.url;
                    linkElement.className = 'text-primary me-3';
                    linkElement.title = link.label;
                    if (link.label !== "personal") {
                        linkElement.textContent = link.label;
                    } else {
                        const displayUrl = link.url.replace(/^https?:\/\//i, '');
                        linkElement.textContent = displayUrl;
                    }
                    linkElement.target = '_blank'; // Open in new tab
                    linksContainer.appendChild(linkElement);
                });
            }
            
            // Update IDs to be unique for each person
            cardClone.querySelectorAll('[id]').forEach(element => {
                if (element.id !== `person-${person.id}`) {
                    element.id = `${element.id}-${person.id}`;
                }
            });
            
            // Add the cloned card to the people container
            peopleContainer.appendChild(cardClone);
        });
        
        // Remove the original template card
        templateCard.parentElement.remove();
        
        // Initialize sorting functionality after people are loaded
        initializeSorting();

        // Hide spinner
        spinner.remove();
        
    } catch (error) {
        console.error('Error loading people data:', error);
        
        // Show an error message in place of the template
        const templateCard = document.getElementById('person');
        if (templateCard) {
            const errorCard = templateCard.cloneNode(true);
            errorCard.querySelector('#firstName').textContent = 'Error';
            errorCard.querySelector('#lastName').textContent = 'Loading Data';
            errorCard.querySelector('#position').textContent = 'System Message';
            errorCard.querySelector('#description').textContent = 'Unable to load people data. Please check the database connection.';
            errorCard.querySelector('#links').innerHTML = '';
            
            templateCard.parentElement.parentElement.appendChild(errorCard.parentElement);
            templateCard.parentElement.remove();
        }
    }
});

// =====================================
// SORTING FUNCTIONALITY
// =====================================

// Local storage key for saving sort preference
const SORT_PREFERENCE_KEY = 'peopleGallerySortPreference';

// Store the original order of cards for consistent random shuffling
let originalCardOrder = [];

function initializeSorting() {
    // Store the original order of cards when first initialized
    const peopleContainer = document.querySelector('#people');
    if (peopleContainer) {
        originalCardOrder = Array.from(peopleContainer.children).filter(card => {
            const personElement = card.querySelector('[id^="person-"]');
            return personElement !== null;
        });
    }
    const sortDropdownItems = document.querySelectorAll('[data-sort]');
    const currentSortSpan = document.getElementById('currentSort');
    
    // Load saved sort preference or default to 'random'
    const savedSort = getSavedSortPreference();
    
    // Apply the saved/default sorting
    if (savedSort) {
        applySorting(savedSort.sortBy);
        if (currentSortSpan) {
            currentSortSpan.textContent = savedSort.label;
        }
    }
    
    // Add click event listeners to all dropdown items
    sortDropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sortBy = this.getAttribute('data-sort');
            const sortLabel = this.textContent;
            
            // Update the current sort display
            if (currentSortSpan) {
                currentSortSpan.textContent = sortLabel;
            }
            
            // Save the sort preference
            saveSortPreference(sortBy, sortLabel);
            
            // Apply the sorting
            applySorting(sortBy);
        });
    });
}

function applySorting(sortBy) {
    const peopleContainer = document.querySelector('.row.g-4');
    if (!peopleContainer) {
        console.error('People container not found');
        return;
    }
    
    // Get all person cards (excluding any non-person elements)
    const personCards = Array.from(peopleContainer.children).filter(card => {
        const personElement = card.querySelector('[id^="person-"]');
        return personElement !== null;
    });
    
    // If originalCardOrder is empty, store the current order
    if (originalCardOrder.length === 0) {
        originalCardOrder = [...personCards];
    }
    
    let sortedCards = [];
    
    switch(sortBy) {
        case 'random':
            // Always shuffle from the original order to get consistent results
            sortedCards = shuffle([...originalCardOrder]);
            break;
            
        case 'firstName':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const firstNameA = a.querySelector('[id^="firstName-"]').textContent.toLowerCase();
                const firstNameB = b.querySelector('[id^="firstName-"]').textContent.toLowerCase();
                return firstNameA.localeCompare(firstNameB);
            });
            break;
            
        case 'firstNameDesc':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const firstNameA = a.querySelector('[id^="firstName-"]').textContent.toLowerCase();
                const firstNameB = b.querySelector('[id^="firstName-"]').textContent.toLowerCase();
                return firstNameB.localeCompare(firstNameA);
            });
            break;
            
        case 'lastName':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const lastNameA = a.querySelector('[id^="lastName-"]').textContent.toLowerCase();
                const lastNameB = b.querySelector('[id^="lastName-"]').textContent.toLowerCase();
                return lastNameA.localeCompare(lastNameB);
            });
            break;
            
        case 'lastNameDesc':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const lastNameA = a.querySelector('[id^="lastName-"]').textContent.toLowerCase();
                const lastNameB = b.querySelector('[id^="lastName-"]').textContent.toLowerCase();
                return lastNameB.localeCompare(lastNameA);
            });
            break;
            
        case 'position':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const positionA = a.querySelector('[id^="position-"]').textContent.toLowerCase();
                const positionB = b.querySelector('[id^="position-"]').textContent.toLowerCase();
                return positionA.localeCompare(positionB);
            });
            break;
            
        case 'positionDesc':
            sortedCards = [...originalCardOrder].sort((a, b) => {
                const positionA = a.querySelector('[id^="position-"]').textContent.toLowerCase();
                const positionB = b.querySelector('[id^="position-"]').textContent.toLowerCase();
                return positionB.localeCompare(positionA);
            });
            break;
            
        default:
            console.error('Unknown sort type:', sortBy);
            return;
    }
    
    // Re-append the sorted cards to the container
    sortedCards.forEach(card => {
        peopleContainer.appendChild(card);
    });
}

// Save sort preference to localStorage
function saveSortPreference(sortBy, label) {
    try {
        const preference = {
            sortBy: sortBy,
            label: label,
            timestamp: Date.now()
        };
        localStorage.setItem(SORT_PREFERENCE_KEY, JSON.stringify(preference));
    } catch (error) {
        console.warn('Failed to save sort preference:', error);
    }
}

// Get saved sort preference from localStorage
function getSavedSortPreference() {
    try {
        const saved = localStorage.getItem(SORT_PREFERENCE_KEY);
        if (saved) {
            const preference = JSON.parse(saved);
            // Return the preference if it's valid
            if (preference.sortBy && preference.label) {
                return preference;
            }
        }
    } catch (error) {
        console.warn('Failed to load sort preference:', error);
    }
    
    // Return default if no valid preference found
    return {
        sortBy: 'random',
        label: 'Daily Random'
    };
}
